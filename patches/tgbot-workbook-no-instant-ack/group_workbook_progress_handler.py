"""工作簿进展：只走 bus。群里不回（Bot API 收不到狂人 bot；主人钦定取消群回复）。

触发源：agent-bus 入站 → T-1 实查 → reply bus。
"""
from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import re
import sys
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
    PROJECT_ROOT,
    TGBOT_DIR,
    WORKER_ANT_BOT,
)

log = logging.getLogger(__name__)

# 主人 2026-09-05：Bot API 收不到狂人 bot 群消息 → 取消群回复，只保留 bus
GROUP_WORKBOOK_REPLY_TO_GROUP = False

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


def _posted_key(message_id: int, *, channel: str = 'group') -> str:
    if channel == 'bus':
        return f'bus:{int(message_id)}'
    return str(int(message_id))


def already_posted_for_date(workbook_date: str) -> bool:
    """群通道当天是否已发过（不含 bus-only）。"""
    with _state_lock():
        rec = (_load_state().get('by_date') or {}).get(workbook_date) or {}
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


def _mark_posted(
    message_id: int,
    workbook_date: str,
    *,
    brief: bool = True,
    detailed: bool = False,
    channel: str = 'group',
    bus_id: int = 0,
) -> None:
    with _state_lock():
        data = _load_state()
        ids = list(data.get('posted_ids') or [])
        key = _posted_key(message_id or bus_id, channel=channel) if (message_id or bus_id) else ''
        if key and key not in ids:
            ids.append(key)
        data['posted_ids'] = ids[-200:]
        by_date = dict(data.get('by_date') or {})
        rec = dict(by_date.get(workbook_date) or {})
        if channel == 'bus':
            rec['bus_sent'] = True
            rec['bus_ts'] = datetime.now(_BJ).isoformat()
            if bus_id:
                rec['bus_id'] = bus_id
                bids = list(rec.get('bus_ids') or [])
                if str(bus_id) not in bids:
                    bids.append(str(bus_id))
                rec['bus_ids'] = bids[-20:]
        else:
            if brief:
                rec['brief'] = True
                rec.pop('brief_inflight', None)
                rec.pop('claimed_at', None)
            if detailed:
                rec['detailed'] = True
            if message_id:
                rec['message_id'] = message_id
        rec['ts'] = datetime.now(_BJ).isoformat()
        by_date[workbook_date] = rec
        data['by_date'] = by_date
        data['last'] = {
            'workbook_date': workbook_date,
            'message_id': message_id,
            'channel': channel,
            'bus_id': bus_id,
        }
        _save_state(data)


def _already_posted(message_id: int, *, channel: str = 'group') -> bool:
    if not message_id:
        return False
    data = _load_state()
    return _posted_key(message_id, channel=channel) in (data.get('posted_ids') or [])


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


async def _build_live_body(text: str, workbook_date: str) -> str | None:
    from workbook_progress_service import (
        _report_cutoff_date,
        build_progress_reply,
        fetch_live_snapshot,
    )

    cutoff = _report_cutoff_date(workbook_date)
    snap = await asyncio.to_thread(fetch_live_snapshot, force=True, cutoff_dt=cutoff)
    full_text = load_full_workbook_text(workbook_date) or text
    return build_progress_reply(full_text, snap=snap, workbook_date=workbook_date)


def _send_bus_reply(body: str, *, bus_id: int) -> dict:
    notify = str(Path(PROJECT_ROOT) / '.claude' / 'database' / 'scripts' / 'notify')
    if notify not in sys.path:
        sys.path.insert(0, notify)
    from agent_bus_send import send as bus_send  # noqa: WPS433

    try:
        return bus_send(
            from_agent='youchu_ai',
            to_agent='worker_ant',
            text=body,
            reply_to_bus_id=int(bus_id),
            kind='reply',
            payload={'kind': 'reply', 'topic': 'workbook_progress'},
        )
    except SystemExit as exc:
        return {'ok': False, 'error': str(exc)}


async def post_workbook_pipeline(
    application,
    *,
    text: str,
    msg_id: int = 0,
    source: str = '',
    skip_if_date_done: bool = True,
    force_repost: bool = False,
) -> bool:
    """群回复已关闭。工作簿进展只走 bus。"""
    del application, msg_id, skip_if_date_done, force_repost
    if text and is_workbook_roll_call(text) and not looks_like_canned_fallback(text):
        save_full_workbook_text(text)
    log.info('[workbook-progress] group reply disabled (bus-only) source=%s', source)
    return False


async def reply_workbook_via_bus(text: str, *, bus_id: int) -> bool:
    """bus 入站后：T-1 实查再 reply。不发群。"""
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        return False
    if not bus_id:
        return False
    if not is_workbook_roll_call(text) or looks_like_canned_fallback(text):
        return False
    if _already_posted(bus_id, channel='bus'):
        log.info('[workbook-progress] skip bus_id=%s already replied', bus_id)
        return False

    save_full_workbook_text(text)
    workbook_date = _workbook_date(text)
    body = await _build_live_body(text, workbook_date)
    if not body:
        return False
    try:
        result = await asyncio.to_thread(_send_bus_reply, body, bus_id=bus_id)
    except Exception:
        log.exception('[workbook-progress] bus reply failed bus_id=%s', bus_id)
        return False
    if not result or not result.get('ok'):
        log.warning('[workbook-progress] bus reply not ok bus_id=%s result=%s', bus_id, result)
        return False
    _mark_posted(0, workbook_date, channel='bus', bus_id=bus_id)
    log.info('[workbook-progress] bus replied date=%s bus_id=%s skipped=%s',
             workbook_date, bus_id, result.get('skipped'))
    return True


def schedule_workbook_pipeline(text: str, *, msg_id: int = 0, source: str = '') -> None:
    """群通道已关：只存原文，不发群。"""
    del msg_id, source
    if is_workbook_roll_call(text) and not looks_like_canned_fallback(text):
        save_full_workbook_text(text)


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
    """不再回群。返回 False，让 bot 旁听后 return，不把工作簿当派活回群。"""
    del update, reply_fn, application
    if text and is_workbook_roll_call(text) and not looks_like_canned_fallback(text):
        save_full_workbook_text(text)
    return False


async def try_workbook_progress_reply(
    application,
    rec: dict,
) -> bool:
    """Telethon 看见群簿也不回群；进展只走 bus。"""
    del application
    text = rec.get('text') or ''
    if text and is_workbook_roll_call(text) and not looks_like_canned_fallback(text):
        save_full_workbook_text(text)
    return False


def is_fallback_stub(text: str) -> bool:
    """定时兜底 stub：能过点名判定，但不含编号【又初】项（避免冒充当日簿）。"""
    t = text or ''
    if parse_youchu_items(t):
        return False
    return '【又初】' in t and bool(re.search(r'今日工作簿|📋|待办', t))


def looks_like_canned_fallback(text: str, for_date: str | None = None) -> bool:
    """自造的旧 1/2 条模板，或无编号 stub。真工作簿即使碰巧含这两项也不会整篇相等。"""
    if is_fallback_stub(text):
        return True
    dt = for_date or _workbook_date(text)
    old = (
        f'📋 今日工作簿 · {dt} 09:00 北京时间\n'
        f'{dt} 待办(项 + 负责人)：\n\n'
        f'1. 页面统计（进入/跳转/跳出） 【又初】\n'
        f'2. 渠道归因影子序列·归因段 【又初】\n\n'
        f'各负责人今天的进展 @worker_ant_bot 报一下'
    )
    return (text or '').strip() == old.strip()


def fallback_workbook_template(for_date: str | None = None) -> str:
    dt = for_date or datetime.now(_BJ).strftime('%Y-%m-%d')
    return (
        f'📋 今日工作簿 · {dt} 09:00 北京时间\n'
        f'{dt} 待办(项 + 负责人)：\n'
        f'【又初】\n'
        f'各负责人今天的进展 @worker_ant_bot 报一下'
    )


def in_daily_fallback_window(now: datetime | None = None) -> bool:
    """09:08–11:59：给 09:00 真簿进站留窗口，避免整点用写死清单秒回。"""
    t = now or datetime.now(_BJ)
    if t.hour < 9 or t.hour > 11:
        return False
    if t.hour == 9 and t.minute < 8:
        return False
    return True


async def maybe_daily_fallback(application) -> None:  # noqa: ARG001
    """已废止：群收不到时禁止闹钟发群。改等 bus 入站后再实查 reply。"""
    return
