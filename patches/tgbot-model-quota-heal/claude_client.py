"""Claude client — API SDK / Cursor Agent API / Claude Code CLI."""
import json
import os
import shutil
import tempfile
import subprocess
import logging
import time
from dataclasses import dataclass
from typing import Callable
import model_quota
from config import (
    ANTHROPIC_API_KEY,
    CURSOR_API_KEY,
    CURSOR_MODEL,
    CURSOR_MODEL_FAST,
    CURSOR_MODEL_LEARN,
    CURSOR_MODEL_SUMMARIZE,
    CURSOR_MODEL_WORK,
    CLAUDE_MODEL,
    MAX_TOKENS,
    PROJECT_ROOT,
    AI_HARD_TIMEOUT_SEC,
    AI_IDLE_TIMEOUT_SEC,
    AI_PROGRESS_INTERVAL_SEC,
)

log = logging.getLogger(__name__)

HeartbeatFn = Callable[[int], None]


@dataclass
class ChatResult:
    text: str
    cursor_chat_id: str | None = None


def has_api_key() -> bool:
    return bool(ANTHROPIC_API_KEY)


def has_cursor_api_key() -> bool:
    return bool(CURSOR_API_KEY)


def mode_name() -> str:
    if has_api_key():
        return "API SDK"
    if has_cursor_api_key():
        return f"Cursor Agent API (work={CURSOR_MODEL_WORK}, fast={CURSOR_MODEL_FAST})"
    return "CLI (OAuth)"


def pick_model(task_type: str = 'chat') -> str:
    """按任务选模型：chat/dispatch 用强模型，summarize/learn/triage 用快模型。"""
    mapping = {
        'chat': CURSOR_MODEL_WORK,
        'dispatch': CURSOR_MODEL_WORK,
        'summarize': CURSOR_MODEL_SUMMARIZE,
        'learn': CURSOR_MODEL_LEARN,
        'triage': CURSOR_MODEL_FAST,
        'fast': CURSOR_MODEL_FAST,
        'heartbeat': CURSOR_MODEL_FAST,
        'ack': CURSOR_MODEL_FAST,
    }
    return mapping.get((task_type or 'chat').lower(), CURSOR_MODEL_WORK)


def _build_history_prompt(messages: list[dict]) -> str:
    if len(messages) <= 1:
        return messages[-1]['content'] if messages else ''
    history = ""
    for m in messages[:-1]:
        role = "用户" if m['role'] == 'user' else "助手"
        history += f"[{role}]: {m['content']}\n\n"
    return f"以下是之前的对话记录：\n\n{history}---\n\n当前问题：{messages[-1]['content']}"


def _build_full_prompt(system_prompt: str, messages: list[dict]) -> str:
    user_prompt = _build_history_prompt(messages)
    if not system_prompt:
        return user_prompt
    return f"{system_prompt}\n\n---\n\n{user_prompt}"


def _write_system_prompt(system_prompt: str) -> str | None:
    if not system_prompt:
        return None
    tmp_dir = os.path.join(tempfile.gettempdir(), 'tgbot')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_file = os.path.join(tmp_dir, f'prompt_{os.getpid()}_{id(system_prompt) % 10000}.md')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(system_prompt)
    return tmp_file


def _cleanup_tmp(tmp_file: str | None):
    if tmp_file and os.path.exists(tmp_file):
        try:
            os.unlink(tmp_file)
        except OSError:
            pass


def _run_subprocess_until_done(
    proc: subprocess.Popen,
    on_chunk: Callable[[str], None],
    *,
    on_heartbeat: HeartbeatFn | None = None,
    progress_interval_sec: int | None = None,
    hard_timeout_sec: int | None = None,
    idle_timeout_sec: int | None = None,
) -> str:
    """读 stdout 直到子进程结束。

    - idle_timeout：连续无 stdout 超过 N 秒 → kill（默认 15min，释放 agent）
    - hard_timeout：墙钟总时长上限（可选）
    - on_heartbeat：仅内部探活回调；默认不向 TG 刷屏
    """
    interval = progress_interval_sec if progress_interval_sec is not None else AI_PROGRESS_INTERVAL_SEC
    hard_cap = hard_timeout_sec if hard_timeout_sec is not None else AI_HARD_TIMEOUT_SEC
    idle_cap = idle_timeout_sec if idle_timeout_sec is not None else AI_IDLE_TIMEOUT_SEC

    accumulated = ""
    buf = ""
    start = time.time()
    last_hb = start
    last_activity = start
    stdout = proc.stdout
    if stdout is None:
        proc.wait()
        return accumulated

    while True:
        now = time.time()
        elapsed = int(now - start)
        if hard_cap > 0 and elapsed >= hard_cap and proc.poll() is None:
            log.warning('[CURSOR] hard timeout %ss → kill pid=%s', hard_cap, proc.pid)
            proc.kill()
            raise subprocess.TimeoutExpired(proc.args, hard_cap)

        idle_for = now - last_activity
        if idle_cap > 0 and idle_for >= idle_cap and proc.poll() is None:
            log.warning(
                '[CURSOR] idle timeout %ss (no stdout) → kill pid=%s elapsed=%ss',
                idle_cap, proc.pid, elapsed,
            )
            proc.kill()
            raise subprocess.TimeoutExpired(proc.args, idle_cap)

        if on_heartbeat and proc.poll() is None and now - last_hb >= interval:
            try:
                on_heartbeat(elapsed)
            except Exception as exc:
                log.warning('[CURSOR] on_heartbeat failed: %s', exc)
            last_hb = now

        char = stdout.read(1)
        if not char:
            if proc.poll() is not None:
                break
            time.sleep(0.2)
            continue

        last_activity = time.time()
        buf += char
        accumulated += char
        if len(buf) >= 200 or char == '\n':
            on_chunk(buf)
            buf = ""
    if buf:
        on_chunk(buf)
    proc.wait(timeout=10)
    return accumulated


# ── API SDK mode ──

def chat_stream_api(system_prompt: str, messages: list[dict], on_chunk: Callable[[str], None]) -> ChatResult:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    accumulated = ""
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            accumulated += text
            on_chunk(text)
    return ChatResult(text=accumulated)


# ── Cursor Agent API mode ──

def _cursor_agent_bin() -> str:
    return shutil.which('cursor-agent') or shutil.which('agent') or 'cursor-agent'


def _run_cursor_agent(
    args: list[str],
    on_chunk: Callable[[str], None],
    on_heartbeat: HeartbeatFn | None = None,
) -> tuple[str, str, int]:
    """跑 cursor-agent；并行读 stderr，避免 PIPE 塞满死锁。返回 (stdout, stderr, rc)。"""
    import threading

    proc = subprocess.Popen(
        args,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=_cursor_env(),
    )
    stderr_chunks: list[str] = []

    def _drain_stderr() -> None:
        if proc.stderr is None:
            return
        try:
            while True:
                line = proc.stderr.readline()
                if not line:
                    break
                stderr_chunks.append(line)
        except Exception:
            pass

    t = threading.Thread(target=_drain_stderr, daemon=True)
    t.start()
    try:
        accumulated = _run_subprocess_until_done(
            proc, on_chunk, on_heartbeat=on_heartbeat,
        )
    except subprocess.TimeoutExpired:
        t.join(timeout=2)
        raise
    t.join(timeout=5)
    rc = proc.returncode if proc.returncode is not None else -1
    return accumulated, ''.join(stderr_chunks).strip(), rc


def chat_stream_cursor(
    system_prompt: str,
    messages: list[dict],
    on_chunk: Callable[[str], None],
    is_superuser: bool = False,
    cursor_chat_id: str | None = None,
    model: str | None = None,
    task_type: str = 'chat',
    on_heartbeat: HeartbeatFn | None = None,
) -> ChatResult:
    latest = messages[-1]['content'] if messages else ''
    primary = model or pick_model(task_type)
    models_to_try = model_quota.fallback_chain(task_type, primary)
    tried: list[str] = []
    last_result = ChatResult(text='')
    last_stderr = ''

    last_fail_kind = 'empty'
    last_fail_detail = ''

    for use_model in models_to_try:
        tried.append(use_model)
        args = [
            _cursor_agent_bin(),
            '--print',
            '--output-format', 'json',
            # headless：信任工作区 + 关沙箱，否则常空退出
            '--trust',
            '--sandbox', 'disabled',
            '--workspace', PROJECT_ROOT,
            '--model', use_model,
        ]
        # TG 无人值守：一律 force，避免工具审批卡住后空输出
        args.append('--force')
        if CURSOR_API_KEY:
            args.extend(['--api-key', CURSOR_API_KEY])
        prompt_file = None
        accumulated = ""
        stderr = ''
        rc = -1
        try:
            if cursor_chat_id and use_model == primary:
                args.extend(['--resume', cursor_chat_id, '-p', latest])
                log.info(
                    f"[CURSOR] resume session={cursor_chat_id[:8]}… model={use_model} q={latest[:50]}",
                )
            else:
                prompt = _build_full_prompt(system_prompt, messages)
                # 长 prompt 走临时文件，避免 argv 过长 / launchd 下空退出
                if len(prompt) > 6000:
                    prompt_file = _write_system_prompt(prompt)
                    args.extend([
                        '-p',
                        f'请先完整阅读并严格执行文件：{prompt_file}\n'
                        f'然后直接回答该文件末尾「当前问题」。不要只复述文件。',
                    ])
                    log.info(
                        f"[CURSOR] new session model={use_model} via file "
                        f"chars={len(prompt)} path={prompt_file}",
                    )
                else:
                    args.extend(['-p', prompt])
                    log.info(
                        f"[CURSOR] new session model={use_model} in {PROJECT_ROOT}: "
                        f"{prompt[:60]}...",
                    )

            accumulated, stderr, rc = _run_cursor_agent(args, on_chunk, on_heartbeat)
            if rc != 0 and stderr:
                log.warning(f"[CURSOR] model={use_model} rc={rc} stderr: {stderr[:500]}")
                last_stderr = stderr
            elif not (accumulated or '').strip():
                log.warning(
                    '[CURSOR] model=%s empty stdout rc=%s stderr_len=%s',
                    use_model, rc, len(stderr or ''),
                )

            result = _parse_cursor_json(accumulated)
            # json 空结果时再试一次 text
            if not (result.text or '').strip() and not (stderr or '').strip():
                text_args = list(args)
                for i, a in enumerate(text_args):
                    if a == '--output-format' and i + 1 < len(text_args):
                        text_args[i + 1] = 'text'
                        break
                acc2, err2, rc2 = _run_cursor_agent(text_args, on_chunk, on_heartbeat)
                if (acc2 or '').strip():
                    log.info('[CURSOR] text-format fallback ok model=%s', use_model)
                    accumulated, stderr, rc = acc2, err2, rc2
                    result = ChatResult(text=acc2.strip())
                elif err2:
                    stderr = err2
                    last_stderr = err2

            parsed_error = ''
            try:
                raw_json = json.loads((accumulated or '').strip() or '{}')
                if isinstance(raw_json, dict) and raw_json.get('is_error'):
                    parsed_error = str(raw_json.get('error') or raw_json.get('result') or '')
            except (json.JSONDecodeError, TypeError):
                parsed_error = ''

            # 只把 stderr / CLI 错误 / 非零退出当成失败通道；
            # 禁止拿成功正文（含中文「额度」）去判额度——会误杀正常回复。
            err_blob = ' '.join(filter(None, [stderr, parsed_error]))
            if not err_blob and rc != 0:
                err_blob = (result.text or accumulated or '')[:500]

            fail_kind = model_quota.classify_failure(err_blob) if err_blob else (
                'empty' if not (result.text or '').strip() else 'other'
            )

            if err_blob and model_quota.is_auth_error(err_blob):
                last_result = ChatResult(
                    text=model_quota.exhausted_user_reply(
                        task_type, tried, kind='auth', detail=err_blob,
                    ),
                    cursor_chat_id=result.cursor_chat_id or cursor_chat_id,
                )
                log.error('[CURSOR] auth failure on %s, stop fallback: %s', use_model, err_blob[:200])
                return last_result

            if err_blob and model_quota.is_quota_error(err_blob):
                model_quota.mark_exhausted(use_model, reason=err_blob[:200])
                last_result = result
                last_fail_kind = 'quota'
                last_fail_detail = err_blob
                log.warning('[CURSOR] quota/limit on %s, trying next model', use_model)
                continue

            if result.text.strip():
                if cursor_chat_id and result.cursor_chat_id is None:
                    result.cursor_chat_id = cursor_chat_id
                if use_model != primary:
                    log.info('[CURSOR] fallback success: %s -> %s', primary, use_model)
                return result

            # 无正文：若 stderr 有内容，带给下一档；勿把空失败统称额度
            if stderr and not result.text.strip():
                last_result = ChatResult(text='')
                last_fail_kind = fail_kind if fail_kind != 'other' else 'empty'
                last_fail_detail = stderr
            else:
                last_result = result
                last_fail_kind = 'empty'
                last_fail_detail = last_fail_detail or f'model={use_model} empty output rc={rc}'

        except subprocess.TimeoutExpired as exc:
            partial = _parse_cursor_json(accumulated)
            secs = int(exc.timeout or 0)
            mins = max(1, secs // 60)
            if AI_IDLE_TIMEOUT_SEC > 0 and secs == AI_IDLE_TIMEOUT_SEC:
                msg = (
                    f'⏰ 任务超过 {mins} 分钟无新输出，已中止并释放 agent'
                    f'（AI_IDLE_TIMEOUT_SEC={secs}）'
                )
            else:
                msg = f'⏰ 任务运行超过 {mins} 分钟已中止（硬上限）'
            last_result = ChatResult(
                text=partial.text or msg,
                cursor_chat_id=partial.cursor_chat_id or cursor_chat_id,
            )
            break
        except Exception as e:
            log.error(f"[CURSOR] model={use_model} error: {e}")
            partial = _parse_cursor_json(accumulated)
            last_result = ChatResult(
                text=partial.text or f'❌ Cursor Agent 调用失败: {e}',
                cursor_chat_id=partial.cursor_chat_id or cursor_chat_id,
            )
            if model_quota.is_auth_error(str(e)):
                return ChatResult(
                    text=model_quota.exhausted_user_reply(
                        task_type, tried, kind='auth', detail=str(e),
                    ),
                    cursor_chat_id=last_result.cursor_chat_id,
                )
            if model_quota.is_quota_error(str(e)):
                model_quota.mark_exhausted(use_model, reason=str(e))
                last_fail_kind = 'quota'
                last_fail_detail = str(e)
                continue
            break
        finally:
            _cleanup_tmp(prompt_file)

    fallback_text = model_quota.ensure_nonempty(
        last_result.text or last_stderr,
        task_type=task_type,
        tried=tried,
        kind=last_fail_kind,
        detail=last_fail_detail or last_stderr,
    )
    return ChatResult(
        text=fallback_text,
        cursor_chat_id=last_result.cursor_chat_id or cursor_chat_id,
    )


def _cursor_env() -> dict:
    env = os.environ.copy()
    if CURSOR_API_KEY:
        env['CURSOR_API_KEY'] = CURSOR_API_KEY
    return env


def _parse_cursor_json(accumulated: str) -> ChatResult:
    raw = (accumulated or '').strip()
    if not raw:
        return ChatResult(text='')
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            text = (data.get('result') or '').strip()
            sid = data.get('session_id')
            if data.get('is_error') and not text:
                text = data.get('error') or raw
            return ChatResult(text=text or raw, cursor_chat_id=sid)
    except json.JSONDecodeError:
        pass
    return ChatResult(text=raw)


# ── Claude Code CLI mode ──

def chat_stream_cli(
    system_prompt: str,
    messages: list[dict],
    on_chunk: Callable[[str], None],
    is_superuser: bool = False,
    on_heartbeat: HeartbeatFn | None = None,
) -> ChatResult:
    prompt = _build_history_prompt(messages)

    args = [
        'claude', '-p', prompt,
        '--print',
        '--output-format', 'text',
    ]

    if is_superuser:
        args.append('--dangerously-skip-permissions')
    else:
        args.extend([
            '--allowedTools',
            'Read', 'Write', 'Edit', 'Glob', 'Grep',
            'WebSearch', 'WebFetch',
            'Bash(cat:*)', 'Bash(ls:*)', 'Bash(head:*)', 'Bash(wc:*)',
            'Bash(mysql:*)', 'Bash(conda:*)',
            'Bash(sqlite3:*)', 'Bash(grep:*)', 'Bash(find:*)',
        ])

    tmp_file = _write_system_prompt(system_prompt)
    if tmp_file:
        args.extend(['--append-system-prompt-file', tmp_file])

    accumulated = ""
    proc = None
    try:
        log.info(f"[CLI] spawning in {PROJECT_ROOT}: {prompt[:60]}...")
        proc = subprocess.Popen(
            args,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        accumulated = _run_subprocess_until_done(
            proc, on_chunk, on_heartbeat=on_heartbeat,
        )
        if proc.returncode != 0:
            stderr = proc.stderr.read()
            if stderr:
                log.warning(f"[CLI] stderr: {stderr[:500]}")
            if not accumulated.strip() and 'Invalid API key' in (stderr or ''):
                return ChatResult(text="❌ Claude CLI 未登录。请在 Mac 终端执行 `claude login`，或在 .env 配置 CURSOR_API_KEY / ANTHROPIC_API_KEY。")
        return ChatResult(text=accumulated.strip())

    except subprocess.TimeoutExpired as exc:
        if proc:
            proc.kill()
        partial = (accumulated or '').strip()
        if partial:
            return ChatResult(text=partial)
        secs = int(exc.timeout or 0)
        mins = max(1, secs // 60)
        if AI_IDLE_TIMEOUT_SEC > 0 and secs == AI_IDLE_TIMEOUT_SEC:
            return ChatResult(
                text=f'⏰ 任务超过 {mins} 分钟无新输出，已中止并释放 agent（AI_IDLE_TIMEOUT_SEC={secs}）'
            )
        return ChatResult(text=f'⏰ 任务运行超过 {mins} 分钟已中止（硬上限）')
    except Exception as e:
        log.error(f"[CLI] error: {e}")
        return ChatResult(text=accumulated.strip() or f"❌ CLI 调用失败: {e}")
    finally:
        _cleanup_tmp(tmp_file)


# ── Unified interface ──

def chat_stream(
    system_prompt: str,
    messages: list[dict],
    on_chunk: Callable[[str], None] = lambda x: None,
    is_superuser: bool = False,
    cursor_chat_id: str | None = None,
    task_type: str = 'chat',
    model: str | None = None,
    on_heartbeat: HeartbeatFn | None = None,
) -> ChatResult:
    use_model = model or pick_model(task_type)
    if has_api_key():
        log.info("[MODE] Streaming via API SDK")
        return chat_stream_api(system_prompt, messages, on_chunk)
    if has_cursor_api_key():
        log.info(f"[MODE] Cursor Agent API task={task_type} model={use_model} superuser={is_superuser}")
        return chat_stream_cursor(
            system_prompt, messages, on_chunk, is_superuser,
            cursor_chat_id=cursor_chat_id,
            model=use_model,
            task_type=task_type,
            on_heartbeat=on_heartbeat,
        )
    log.info(f"[MODE] Streaming via CLI (OAuth), superuser={is_superuser}")
    return chat_stream_cli(system_prompt, messages, on_chunk, is_superuser, on_heartbeat=on_heartbeat)
