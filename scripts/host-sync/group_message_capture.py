"""把真人号已连上的 Telethon 看到的群消息和私聊追加到按日落盘。

不另开 session。第二条客户端会抢走 NewMessage，也会锁住 user_telegram.session。
凌晨学习要读「这个号所在的每一个群、每一条私聊、上一自然日的每一条文字」，
由已连接的客户端按日落历史，不能只靠当天监听到的增量，更不能只读狂人入站。
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from config import TGBOT_DIR

SHANGHAI = ZoneInfo('Asia/Shanghai')
RAW_DIR = os.path.join(TGBOT_DIR, 'data', 'group_raw')
REQUEST_PATH = os.path.join(TGBOT_DIR, 'data', 'group_learn_backfill.request.json')
DONE_PATH = os.path.join(TGBOT_DIR, 'data', 'group_learn_backfill.done.json')

_lock = threading.Lock()
_seen: dict[str, set[str]] = {}


def _day_of(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(SHANGHAI).strftime('%Y-%m-%d')


def _seen_for(day: str) -> set[str]:
    keys = _seen.get(day)
    if keys is not None:
        return keys
    keys = set()
    path = os.path.join(RAW_DIR, f'{day}.jsonl')
    if os.path.isfile(path):
        with open(path, encoding='utf-8') as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                mid = rec.get('message_id')
                if mid is None:
                    continue
                keys.add(f"{rec.get('chat_id')}:{mid}")
    _seen[day] = keys
    return keys


def append_record(rec: dict) -> str | None:
    """写入返回路径；同一群同一 message_id 已在盘上则返回空串。"""
    text = (rec.get('text') or '').strip()
    if not text:
        return None
    ts = rec.get('ts') or ''
    try:
        when = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except ValueError:
        when = datetime.now(timezone.utc)
    day = _day_of(when)
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, f'{day}.jsonl')
    line = {
        'ts': when.astimezone(SHANGHAI).strftime('%Y-%m-%d %H:%M:%S'),
        'ts_utc': when.astimezone(timezone.utc).isoformat(),
        'chat_id': rec.get('chat_id'),
        'chat_kind': rec.get('chat_kind') or 'group',
        'chat_title': (rec.get('chat_title') or '')[:80],
        'message_id': rec.get('message_id'),
        'sender_id': rec.get('sender_id'),
        'sender_username': (rec.get('sender_username') or '')[:64],
        'sender_name': (rec.get('sender_name') or '')[:64],
        'text': text[:4000],
    }
    mid = line.get('message_id')
    key = f"{line.get('chat_id')}:{mid}" if mid is not None else ''
    with _lock:
        if key:
            seen = _seen_for(day)
            if key in seen:
                return ''
            seen.add(key)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(line, ensure_ascii=False) + '\n')
    return path


def write_done(payload: dict) -> None:
    os.makedirs(os.path.dirname(DONE_PATH), exist_ok=True)
    tmp = DONE_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    os.replace(tmp, DONE_PATH)


def _entity_kind(entity) -> str:
    """group=普通群或超级群；private=真人私聊。频道广播和机器人对话不收。"""
    if entity is None:
        return ''
    name = type(entity).__name__
    if name == 'User':
        if getattr(entity, 'bot', False):
            return ''
        return 'private'
    if name == 'Chat':
        return 'group'
    if name == 'Channel' and getattr(entity, 'megagroup', False):
        return 'group'
    return ''


def _chat_title(entity, kind: str) -> str:
    if kind == 'private':
        name = ' '.join(
            p for p in (getattr(entity, 'first_name', None), getattr(entity, 'last_name', None)) if p
        )
        name = name or getattr(entity, 'username', None) or str(getattr(entity, 'id', '') or '')
        return f'私聊·{name}'[:80]
    return (getattr(entity, 'title', None) or '')[:80]


def append_event(event) -> str | None:
    """Telethon NewMessage。收普通群、超级群和真人私聊，不收频道广播、不收服务消息。"""
    chat = getattr(event, 'chat', None)
    kind = _entity_kind(chat) if chat is not None else ''
    if not kind and getattr(event, 'is_private', False):
        kind = 'private'
    if not kind and getattr(event, 'is_group', False):
        kind = 'group'
    if not kind:
        return None
    msg = getattr(event, 'message', None)
    if msg is None or getattr(msg, 'action', None):
        return None
    text = (getattr(msg, 'message', None) or getattr(msg, 'text', None) or '').strip()
    if not text:
        return None
    when = getattr(msg, 'date', None) or datetime.now(timezone.utc)
    chat = getattr(event, 'chat', None)
    sender = getattr(event, 'sender', None)
    username = ''
    name = ''
    if sender is not None:
        username = getattr(sender, 'username', None) or ''
        name = ' '.join(
            p for p in (getattr(sender, 'first_name', None), getattr(sender, 'last_name', None)) if p
        )
    return append_record({
        'ts': when.isoformat() if hasattr(when, 'isoformat') else str(when),
        'chat_id': getattr(event, 'chat_id', None),
        'chat_kind': kind,
        'chat_title': _chat_title(chat, kind) if chat is not None else '',
        'message_id': getattr(msg, 'id', None),
        'sender_id': getattr(event, 'sender_id', None),
        'sender_username': username,
        'sender_name': name,
        'text': text,
    })


async def backfill_day(client, day: str) -> dict:
    """用已经连着的客户端，把这个号当前所在的每个群和每条私聊、该上海日的文字全部落盘。"""
    start = datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=SHANGHAI)
    end = start + timedelta(days=1)
    old_flood = getattr(client, 'flood_sleep_threshold', 60)
    client.flood_sleep_threshold = max(int(old_flood or 0), 180)
    groups = 0
    privates = 0
    scanned = 0
    written = 0
    per_chat: dict[str, int] = {}
    sender_cache: dict = {}
    try:
        me = await client.get_me()
        me_id = getattr(me, 'id', None)
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            kind = _entity_kind(entity)
            if not kind:
                continue
            if kind == 'private' and getattr(entity, 'id', None) == me_id:
                continue
            if kind == 'private':
                privates += 1
            else:
                groups += 1
            title = _chat_title(entity, kind)
            chat_id = dialog.id
            n = 0
            async for msg in client.iter_messages(entity, offset_date=end):
                when = getattr(msg, 'date', None)
                if when is None:
                    continue
                if when.tzinfo is None:
                    when = when.replace(tzinfo=timezone.utc)
                local = when.astimezone(SHANGHAI)
                if local < start:
                    break
                if local >= end or getattr(msg, 'action', None):
                    continue
                text = (getattr(msg, 'message', None) or '').strip()
                if not text:
                    continue
                scanned += 1
                n += 1
                username, name = await _sender_names(msg, sender_cache)
                saved = append_record({
                    'ts': when.isoformat(),
                    'chat_id': chat_id,
                    'chat_kind': kind,
                    'chat_title': title,
                    'message_id': getattr(msg, 'id', None),
                    'sender_id': getattr(msg, 'sender_id', None),
                    'sender_username': username,
                    'sender_name': name,
                    'text': text,
                })
                if saved:
                    written += 1
            per_chat[title or str(chat_id)] = n
    finally:
        client.flood_sleep_threshold = old_flood
    return {
        'day': day,
        'groups': groups,
        'privates': privates,
        'scanned': scanned,
        'written': written,
        'per_chat': per_chat,
    }


async def _sender_names(msg, cache: dict) -> tuple[str, str]:
    sid = getattr(msg, 'sender_id', None)
    if sid in cache:
        return cache[sid]
    sender = getattr(msg, 'sender', None)
    if sender is None and sid:
        try:
            sender = await msg.get_sender()
        except Exception:
            sender = None
    username = ''
    name = ''
    if sender is not None:
        username = getattr(sender, 'username', None) or ''
        name = ' '.join(
            p for p in (getattr(sender, 'first_name', None), getattr(sender, 'last_name', None)) if p
        )
        if not name:
            name = getattr(sender, 'title', None) or ''
    cache[sid] = (username, name)
    return cache[sid]
