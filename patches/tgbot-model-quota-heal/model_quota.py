"""模型额度/限流检测、本地记帐与 fallback 链（避免 token 用尽后静默）。

硬规则：
- 只有 API/CLI 错误形态才算额度；正常中文回复里出现「额度/用尽」不算失败
- 鉴权失败、空输出不要冒充「额度用尽」
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime

from config import (
    CURSOR_MODEL,
    CURSOR_MODEL_FALLBACK_CHAIN,
    CURSOR_MODEL_FAST,
    CURSOR_MODEL_LEARN,
    CURSOR_MODEL_SUMMARIZE,
    CURSOR_MODEL_WORK,
    MODEL_QUOTA_RESET_HOURS,
    TGBOT_DIR,
)

log = logging.getLogger(__name__)

STATE_PATH = os.path.join(TGBOT_DIR, 'data', 'model_quota_state.json')

# 最终兜底：备用链全挂后仍再试 auto，任务不能停在空回
LAST_RESORT_MODEL = 'auto'

# 仅匹配 API/CLI 报错形态；禁止裸配中文「额度|用尽」（会误伤正常回复）
_QUOTA_PATTERNS = re.compile(
    r'(resource[_ ]?exhausted|rate[\s_-]?limit|too many requests|'
    r'usage limit(?: exceeded)?|limit exceeded|billing|out of (?:tokens|credits)|'
    r'insufficient[_ ]?(?:quota|credit|balance)|'
    r'\b429\b|token.?limit|max.?usage|'
    r'model (?:is )?not available|unavailable for your (?:plan|tier|account)|'
    r'quota exceeded|exceeded your.*quota)',
    re.IGNORECASE,
)

_AUTH_PATTERNS = re.compile(
    r'(authentication required|not (?:logged|authenticated)|unauthorized|'
    r'invalid (?:api )?key|api key.*(?:invalid|expired|revoked)|'
    r'please run [\'"]?agent login|cursor[_-]?api[_-]?key|'
    r'auth(?:entication)? (?:failed|error)|401\b|403\b)',
    re.IGNORECASE,
)


def is_quota_error(text: str) -> bool:
    return bool(_QUOTA_PATTERNS.search(text or ''))


def is_auth_error(text: str) -> bool:
    return bool(_AUTH_PATTERNS.search(text or ''))


def classify_failure(text: str) -> str:
    """返回 auth | quota | empty | other。"""
    t = (text or '').strip()
    if not t:
        return 'empty'
    if is_auth_error(t):
        return 'auth'
    if is_quota_error(t):
        return 'quota'
    return 'other'


def _load_state() -> dict:
    if not os.path.isfile(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(data: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _purge_expired(data: dict) -> dict:
    now = time.time()
    ttl = MODEL_QUOTA_RESET_HOURS * 3600
    models = data.get('exhausted') or {}
    if not isinstance(models, dict):
        return {'exhausted': {}}
    kept = {
        m: ts for m, ts in models.items()
        if isinstance(ts, (int, float)) and now - float(ts) < ttl
    }
    return {'exhausted': kept}


def is_exhausted(model: str) -> bool:
    if not model:
        return False
    data = _purge_expired(_load_state())
    return model in (data.get('exhausted') or {})


def mark_exhausted(model: str, *, reason: str = '') -> None:
    if not model:
        return
    data = _purge_expired(_load_state())
    exhausted = data.setdefault('exhausted', {})
    exhausted[model] = time.time()
    data['last_mark'] = {
        'model': model,
        'reason': (reason or '')[:300],
        'at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    _save_state(data)
    log.warning('[model_quota] marked exhausted: %s (%s)', model, reason[:120])


def clear_exhausted() -> None:
    """清本地额度记帐（额度恢复或误判后用）。"""
    _save_state({'exhausted': {}, 'cleared_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    log.info('[model_quota] cleared exhausted marks')


def fallback_chain(task_type: str, primary: str) -> list[str]:
    """按任务类型拼 fallback 链，跳过本地标记为额度用尽的模型。

    末尾始终再挂一次 auto（可与 primary 重复）：前面挂了也要再试，避免任务停滞。
    """
    tt = (task_type or 'chat').lower()
    candidates: list[str] = [primary]

    if tt in ('learn', 'triage'):
        candidates.extend([CURSOR_MODEL_LEARN, CURSOR_MODEL_FAST, CURSOR_MODEL])
    elif tt in ('summarize', 'fast'):
        candidates.extend([CURSOR_MODEL_SUMMARIZE, CURSOR_MODEL_FAST, CURSOR_MODEL])
    else:
        candidates.extend([CURSOR_MODEL_WORK, CURSOR_MODEL_FAST, CURSOR_MODEL])

    candidates.extend(CURSOR_MODEL_FALLBACK_CHAIN)

    seen: set[str] = set()
    ordered: list[str] = []
    for m in candidates:
        m = (m or '').strip()
        if m and m not in seen:
            seen.add(m)
            ordered.append(m)

    available = [m for m in ordered if not is_exhausted(m)]
    chain = available if available else list(ordered)
    if not chain or chain[-1] != LAST_RESORT_MODEL:
        chain = list(chain) + [LAST_RESORT_MODEL]
    return chain


def exhausted_user_reply(
    task_type: str,
    tried: list[str],
    *,
    kind: str = 'quota',
    detail: str = '',
) -> str:
    """保底文案（绝不返回空给需要回复的任务）。按真实失败类型措辞。"""
    tt = (task_type or 'chat').lower()
    if tt in ('learn',):
        return ''
    chain = ' → '.join(tried) if tried else '（无）'
    snippet = re.sub(r'\s+', ' ', (detail or '').strip())[:160]
    if kind == 'auth':
        msg = (
            f'⚠️ Cursor Agent 鉴权失败（已依次尝试: {chain}）。'
            f'请在旧机检查 CURSOR_API_KEY / 执行 cursor-agent login。'
        )
    elif kind == 'empty':
        msg = (
            f'⚠️ Cursor Agent 连续无有效输出（已依次尝试: {chain}；末档已再试 auto）。'
            f'多半是鉴权、模型名或本机 agent 异常，不是网页用量面板耗尽。'
        )
    elif kind == 'quota':
        msg = (
            f'⚠️ AI 模型额度可能已用尽（已依次尝试: {chain}；末档已再试 auto）。'
            f'消息已收到；心跳/查数/SQL 仍可用，复杂任务请稍后再试或联系管理员。'
        )
    else:
        msg = (
            f'⚠️ Cursor Agent 调用失败（已依次尝试: {chain}；末档已再试 auto）。'
            f'消息已收到；心跳/查数/SQL 仍可用。'
        )
    if snippet and kind != 'quota':
        msg += f' 详情: {snippet}'
    return msg


def ensure_nonempty(
    text: str,
    *,
    task_type: str,
    tried: list[str],
    kind: str | None = None,
    detail: str = '',
) -> str:
    t = (text or '').strip()
    if t and t != '(无输出)':
        # 若正文本身就是鉴权/空失败提示，保留；勿再盖成「额度用尽」
        return t
    fail_kind = kind or classify_failure(detail) or 'empty'
    return exhausted_user_reply(
        task_type, tried, kind=fail_kind, detail=detail or text,
    ) or t or '(无输出)'
