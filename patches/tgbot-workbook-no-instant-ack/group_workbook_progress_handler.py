"""群聊工作簿点名：T-1 实查后再发**一条**进展（禁止精简秒回）。

触发源（任一）：
- Bot 群旁听（知秋/狂人人工发工作簿）
- Telethon dispatch（worker_ant_bot 发群，需 session）
- tg_status / 定时兜底（Bot API 收不到其他 bot 时）
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import re
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from zoneinfo import ZoneInfo

import group_roll_call_handler
from config import (
    GROUP_WORKBOOK_PROGRESS_ENABLED,
    MONITOR_GROUP_CHAT_ID,
    TGBOT_DIR,
    WORKER_ANT_BOT,
)

log = logging.getLogger(__name__)

_BJ = ZoneInfo('Asia/Shanghai')
_COOLDOWN_SEC = 3600
_last_post: dict[tuple[int, int], float] = {}
_STATE_PATH = Path(TGBOT_DIR) / 'data' / 'workbook_progress_posted.json'
_LOCK_PATH = Path(TGBOT_DIR) / 'data' / 'workbook_progress_posted.lock'
_FULL_TEXT_PATH = Path(TGBOT_DIR) / 'data' / 'workbook_last_full.json'
_DATE_COOLDOWN_SEC = 120

_PROGRESS_TRIGGER_RE = re.compile(
    r'各负责人.{0,24}进展|进展.{0,12}报一下|报一下.{0,12}进展|'
    r'今日工作簿|工作簿.{0,20}待办|📋|'
    r'@worker_ant_bot.{0,12}报',
    re.I,
)
_WORKBOOK_ITEM_RE = re.compile(
    r'^\s*(\d+)[）).、]\s*(.+?)\s*【\s*(?:又初|初儿)(?:[^】]{0,16})?\s*】\s*$',
    re.M,
)
_DATE_IN_TEXT_RE = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
_DEFAULT_ITEMS = (
    {'no': 3, 'title': '归因表动态跟踪 + 开启归因', 'assignee': '又初'},
    {'no': 4, 'title': '用户标签数据跟踪 + 设备标签设计开发', 'assignee': '又初'},
)

_app_ref = None


def set_application(app) -> None:
    global _app_ref
    _app_ref = app


class TaskStatus(str, Enum):
    DONE = '完成'
    IN_PROGRESS = '进行中'
    NOT_STARTED = '没开始'


@dataclass
class ItemStatus:
    status: TaskStatus
    note: str = ''


def is_authority_sender_username(username: str) -> bool:
    u = (username or '').strip().lower().lstrip('@')
    if not u:
        return False
    if WORKER_ANT_BOT.lower() in u:
        return True
    from config import GROUP_ROLL_CALL_SENDERS
    for token in GROUP_ROLL_CALL_SENDERS:
        t = token.strip().lower().lstrip('@')
        if t and t in u:
            return True
    return False


def parse_youchu_items(text: str) -> list[dict]:
    items: list[dict] = []
    for m in _WORKBOOK_ITEM_RE.finditer(text or ''):
        line = m.group(0)
        assignee = '初儿' if '初儿' in line else '又初'
        items.append({
            'no': int(m.group(1)),
            'title': m.group(2).strip(),
            'assignee': assignee,
        })
    return items


def _workbook_date(text: str) -> str:
    m = _DATE_IN_TEXT_RE.search(text or '')
    if m:
        return f'{m.group(1)}-{m.group(2)}-{m.group(3)}'
    return datetime.now(_BJ).strftime('%Y-%m-%d')


def is_workbook_roll_call(text: str) -> bool:
    """宽松判定：有又初负责项 + 工作簿/进展点名特征（含 tg_status 截断）。"""
    t = text or ''
    items = parse_youchu_items(t)
    if items:
        if _PROGRESS_TRIGGER_RE.search(t):
            return True
        if re.search(r'待办.{0,12}负责人|07-\d{2}.{0,8}待办', t):
            return True
        return False
    # 截断镜像：正文被切掉但仍含又初条目行
    if '【又初】' in t and re.search(r'今日工作簿|📋|待办', t):
        return True
    return False


def is_progress_roll_call(text: str) -> bool:
    return is_workbook_roll_call(text)


def save_full_workbook_text(text: str) -> str:
    dt = _workbook_date(text)
    try:
        _FULL_TEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _FULL_TEXT_PATH.write_text(
            json.dumps({'date': dt, 'text': text, 'ts': datetime.now(_BJ).isoformat()}, ensure_ascii=False),
            encoding='utf-8',
        )
    except OSError:
        pass
    return dt


def load_full_workbook_text(preferred_date: str | None = None) -> str:
    try:
        if _FULL_TEXT_PATH.is_file():
            data = json.loads(_FULL_TEXT_PATH.read_text(encoding='utf-8'))
            if preferred_date and data.get('date') != preferred_date:
                pass
            else:
                return data.get('text') or ''
    except (OSError, json.JSONDecodeError):
        pass
    return ''


@contextmanager
def _state_lock():
    """跨进程互斥：bot 守护进程 + 手动脚本共用同一 state。"""
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK_PATH.open('a+', encoding='utf-8') as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)


def _load_state() -> dict:
    if not _STATE_PATH.is_file():
        return {'posted_ids': [], 'by_date': {}}
    try:
        return json.loads(_STATE_PATH.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {'posted_ids': [], 'by_date': {}}


def _save_state(data: dict) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def already_posted_for_date(workbook_date: str) -> bool:
    with _state_lock():
        by_date = _load_state().get('by_date') or {}
        rec = by_date.get(workbook_date) or {}
        return bool(rec.get('brief') or rec.get('brief_inflight'))


def _try_claim_brief_slot(workbook_date: str, *, force: bool = False) -> bool:
    """原子占位：同一天只允许一条精简链路（含 inflight）。"""
    with _state_lock():
        data = _load_state()
        by_date = dict(data.get('by_date') or {})
        rec = dict(by_date.get(workbook_date) or {})
        if rec.get('brief') or rec.get('brief_inflight'):
            if not force:
                return False
        rec['brief_inflight'] = True
        rec['claimed_at'] = datetime.now(_BJ).isoformat()
        by_date[workbook_date] = rec
        data['by_date'] = by_date
        _save_state(data)
        return True


def _release_brief_inflight(workbook_date: str) -> None:
    with _state_lock():
        data = _load_state()
        by_date = dict(data.get('by_date') or {})
        rec = dict(by_date.get(workbook_date) or {})
        rec.pop('brief_inflight', None)
        rec.pop('claimed_at', None)
        by_date[workbook_date] = rec
        data['by_date'] = by_date
        _save_state(data)


def _mark_posted(message_id: int, workbook_date: str, *, brief: bool = True, detailed: bool = False) -> None:
    with _state_lock():
        data = _load_state()
        ids = list(data.get('posted_ids') or [])
        if message_id and str(message_id) not in ids:
            ids.append(str(message_id))
        data['posted_ids'] = ids[-200:]
        by_date = dict(data.get('by_date') or {})
        rec = dict(by_date.get(workbook_date) or {})
        if brief:
            rec['brief'] = True
            rec.pop('brief_inflight', None)
            rec.pop('claimed_at', None)
        if detailed:
            rec['detailed'] = True
        rec['ts'] = datetime.now(_BJ).isoformat()
        if message_id:
            rec['message_id'] = message_id
        by_date[workbook_date] = rec
        data['by_date'] = by_date
        data['last'] = {'workbook_date': workbook_date, 'message_id': message_id}
        _save_state(data)


def _already_posted(message_id: int) -> bool:
    if not message_id:
        return False
    data = _load_state()
    return str(message_id) in (data.get('posted_ids') or [])


def _cooldown_ok(chat_id: int, dedupe_key: str) -> bool:
    """同进程内短冷却；跨进程靠 _try_claim_brief_slot。"""
    key = (chat_id, dedupe_key)
    now = time.time()
    last = _last_post.get(key, 0.0)
    window = _DATE_COOLDOWN_SEC if dedupe_key.startswith('date:') else _COOLDOWN_SEC
    if now - last < window:
        return False
    _last_post[key] = now
    return True


def build_progress_reply(text: str) -> str | None:
    """兼容旧脚本：单条 T-1 实查进展（无秒回）。"""
    from workbook_progress_service import build_progress_reply as _build
    full = load_full_workbook_text(_workbook_date(text)) or text
    return _build(full)


async def _send_group_messages(application, chat_id: int, parts: list[str]) -> None:
    bot = application.bot
    for part in parts:
        await bot.send_message(chat_id=chat_id, text=part, disable_web_page_preview=True)


async def post_workbook_pipeline(
    application,
    *,
    text: str,
    msg_id: int = 0,
    source: str = '',
    skip_if_date_done: bool = True,
    force_repost: bool = False,
) -> bool:
    """先 T-1 实查，再发一条进展；禁止精简秒回 / 双条 follow-up。"""
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        return False
    if not is_workbook_roll_call(text):
        return False

    save_full_workbook_text(text)
    workbook_date = _workbook_date(text)
    if skip_if_date_done and already_posted_for_date(workbook_date) and not force_repost:
        log.info('[workbook-progress] skip date=%s already posted', workbook_date)
        return False
    if msg_id and _already_posted(msg_id):
        log.info('[workbook-progress] skip msg_id=%s', msg_id)
        return False
    if not _cooldown_ok(MONITOR_GROUP_CHAT_ID, f'date:{workbook_date}'):
        log.info('[workbook-progress] skip date=%s cooldown', workbook_date)
        return False
    if not _try_claim_brief_slot(workbook_date, force=force_repost):
        log.info('[workbook-progress] skip date=%s claim failed', workbook_date)
        return False

    from workbook_progress_service import (
        _report_cutoff_date,
        build_progress_reply,
        fetch_live_snapshot,
        split_for_telegram,
    )

    cutoff = _report_cutoff_date(workbook_date)
    # 实查可能要数十秒：先查完再发，观感是「慢回真进度」，不是秒回罐头
    snap = await asyncio.to_thread(fetch_live_snapshot, force=True, cutoff_dt=cutoff)
    full_text = load_full_workbook_text(workbook_date) or text
    body = build_progress_reply(full_text, snap=snap, workbook_date=workbook_date)
    if not body:
        _release_brief_inflight(workbook_date)
        return False

    try:
        await _send_group_messages(
            application,
            MONITOR_GROUP_CHAT_ID,
            split_for_telegram(body),
        )
    except Exception:
        _release_brief_inflight(workbook_date)
        raise
    _mark_posted(msg_id, workbook_date, brief=True, detailed=True)
    log.info(
        '[workbook-progress] posted date=%s cutoff=%s source=%s msg_id=%s',
        workbook_date, cutoff, source, msg_id,
    )
    return True


def schedule_workbook_pipeline(text: str, *, msg_id: int = 0, source: str = '') -> None:
    """从同步上下文（tg_status 写入等）调度。"""
    if not is_workbook_roll_call(text):
        return
    app = _app_ref
    if not app:
        log.warning('[workbook-progress] app not ready, queued date=%s', _workbook_date(text))
        save_full_workbook_text(text)
        return
    asyncio.create_task(
        post_workbook_pipeline(app, text=text, msg_id=msg_id, source=source),
    )


async def _post_workbook_reply(
    *,
    chat_id: int,
    text: str,
    msg_id: int,
    application,
    log_tag: str,
) -> bool:
    if not is_workbook_roll_call(text):
        return False
    if chat_id != MONITOR_GROUP_CHAT_ID:
        return False
    ok = await post_workbook_pipeline(
        application,
        text=text,
        msg_id=msg_id,
        source=log_tag,
    )
    return ok


async def try_proactive_workbook_reply(
    update,
    *,
    text: str,
    reply_fn,
    application=None,
) -> bool:
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        return False
    chat = update.effective_chat
    if not chat or chat.id != MONITOR_GROUP_CHAT_ID:
        return False
    user = update.effective_user
    if not group_roll_call_handler.is_authority_sender(user):
        uname = (getattr(user, 'username', None) or '').strip().lower()
        if not is_authority_sender_username(uname):
            return False
    msg = update.message or update.effective_message
    msg_id = int(getattr(msg, 'message_id', 0) or 0)
    app = application or _app_ref
    if not app:
        await reply_fn(build_progress_reply(text) or '')
        return True
    return await _post_workbook_reply(
        chat_id=chat.id,
        text=text,
        msg_id=msg_id,
        application=app,
        log_tag='proactive',
    )


async def try_workbook_progress_reply(
    application,
    rec: dict,
) -> bool:
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        return False
    chat_id = int(rec.get('chat_id') or 0)
    if chat_id != MONITOR_GROUP_CHAT_ID:
        return False
    sender = (rec.get('sender_username') or WORKER_ANT_BOT).strip().lower()
    if not is_authority_sender_username(sender):
        return False
    text = rec.get('text') or ''
    msg_id = int(rec.get('message_id') or 0)
    return await _post_workbook_reply(
        chat_id=chat_id,
        text=text,
        msg_id=msg_id,
        application=application,
        log_tag='telethon',
    )


def fallback_workbook_template(for_date: str | None = None) -> str:
    dt = for_date or datetime.now(_BJ).strftime('%Y-%m-%d')
    return (
        f'📋 今日工作簿 · {dt} 09:00 北京时间\n'
        f'{dt} 待办(项 + 负责人)：\n\n'
        f'1. 页面统计（进入/跳转/跳出） 【又初】\n'
        f'2. 渠道归因影子序列·归因段 【又初】\n\n'
        f'各负责人今天的进展 @worker_ant_bot 报一下'
    )


def in_daily_fallback_window(now: datetime | None = None) -> bool:
    """09:01–11:59 北京时间：Bot API 收不到 worker_ant_bot 工作簿时的兜底窗口。"""
    t = now or datetime.now(_BJ)
    if t.hour < 9 or t.hour > 11:
        return False
    if t.hour == 9 and t.minute < 1:
        return False
    return True


async def maybe_daily_fallback(application) -> None:
    """Bot API 收不到 worker_ant_bot 时的定时兜底。"""
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        return
    now = datetime.now(_BJ)
    if not in_daily_fallback_window(now):
        return
    today = now.strftime('%Y-%m-%d')
    if already_posted_for_date(today):
        return
    text = load_full_workbook_text(today) or fallback_workbook_template(today)
    await post_workbook_pipeline(
        application,
        text=text,
        msg_id=0,
        source='daily_fallback',
        skip_if_date_done=True,
    )
