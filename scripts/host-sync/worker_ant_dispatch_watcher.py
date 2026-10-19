"""监听群里 @worker_ant_bot 派单 → 私聊通知 + 自动学习沉淀。"""
from __future__ import annotations

import asyncio
import html
import json
import logging
import os
from datetime import datetime, timezone

from telegram.ext import Application

from config import (
    AGENT_BUS_INCOMING_ONLY,
    AGENT_BUS_STATUS_MIRROR,
    ATTENDANCE_CHECK_CHAT_ID,
    ATTENDANCE_CHECK_ENABLED,
    ATTENDANCE_CHECK_USERNAME,
    MONITOR_GROUP_CHAT_ID,
    TASK_DISPATCH_NOTIFY_USER_IDS,
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    TG_VISIBLE_ONLINE_ENABLED,
    USER_SESSION_PATH,
    WORKER_ANT_BOT,
    WORKER_ANT_DISPATCH_ENABLED,
    WORKER_ANT_INBOX_PATH,
    WORKER_ANT_LEARN_ENABLED,
)
import attendance_check_handler
import group_roll_call_handler
import group_workbook_progress_handler
import group_reply_style
import tg_visible_online
from worker_ant_client import _client_kwargs, session_ready
from worker_ant_learner import learn_from_record
from group_target_filter import message_targets_youchu
from tg_task_tracker import notify_incoming as tracker_notify_incoming
from task_provenance import complete_task, register_task

log = logging.getLogger(__name__)

_telethon_client = None


def telethon_session_ready() -> bool:
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        return False
    return session_ready()


def dispatch_watcher_ready() -> bool:
    if not WORKER_ANT_DISPATCH_ENABLED:
        return False
    if not telethon_session_ready():
        return False
    if not TASK_DISPATCH_NOTIFY_USER_IDS:
        return False
    return True


def telethon_watcher_should_start() -> bool:
    if not telethon_session_ready():
        return False
    if ATTENDANCE_CHECK_ENABLED:
        return True
    if TG_VISIBLE_ONLINE_ENABLED:
        return True
    return dispatch_watcher_ready()


def _append_inbox(record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with open(WORKER_ANT_INBOX_PATH, "a", encoding="utf-8") as f:
        f.write(line)


def _record_from_event(event, worker_id: int) -> dict | None:
    msg = event.message
    if not msg or not event.sender_id or event.sender_id != worker_id:
        return None
    text = (getattr(msg, "message", None) or getattr(msg, "text", None) or "").strip()
    if not text and not msg.media:
        return None
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "chat_id": event.chat_id,
        "message_id": msg.id,
        "sender_id": event.sender_id,
        "sender_username": WORKER_ANT_BOT,
        "text": text,
        "has_media": bool(msg.media),
        "reply_to_msg_id": getattr(msg, "reply_to_msg_id", None),
    }


def _format_dispatch_notice(rec: dict, learn_result: dict | None = None) -> str:
    body = html.escape(rec["text"] or "（无文字，可能含附件）")
    lines = [
        "📋 <b>工作狂人派单</b>",
        f"群 <code>{rec['chat_id']}</code> · msg <code>{rec['message_id']}</code>",
        "━━━━━━━━━━━━",
        body,
        "━━━━━━━━━━━━",
    ]
    if AGENT_BUS_INCOMING_ONLY or AGENT_BUS_STATUS_MIRROR:
        return "\n".join(lines)
    if learn_result and WORKER_ANT_LEARN_ENABLED and not learn_result.get('skipped'):
        lids = learn_result.get('lesson_ids') or []
        summary = (learn_result.get('summary') or '').strip()
        if summary:
            lines.append(f"🧠 <b>已整理记忆</b>\n{html.escape(summary[:800])}")
        if lids:
            lines.append(f"📚 入库 lesson：{', '.join(f'#{i}' for i in lids)}")
        lines.append("后续开发 prompt 会自动带上这些经验。")
    else:
        lines.append("请又初处理；可在 Cursor 继续跟进。")
    return "\n".join(lines)


async def _notify_assignees(application: Application, rec: dict, prov: dict, learn_result: dict | None = None) -> None:
    body = rec.get('text') or ''
    if not message_targets_youchu(body):
        log.info(
            '[dispatch] observe-only group msg_id=%s (not for 又初, skip private mirror)',
            rec.get('message_id'),
        )
        return
    if AGENT_BUS_STATUS_MIRROR:
        await tracker_notify_incoming(
            application,
            channel='worker_ant_group',
            task_label=prov['label'],
            body=rec.get('text') or '',
            header='工作狂人 · 群派单',
            extra_lines=[
                f"群 {rec.get('chat_id')} · msg {rec.get('message_id')}",
            ],
        )
        return
    text = _format_dispatch_notice(rec, learn_result)
    bot = application.bot
    for uid in TASK_DISPATCH_NOTIFY_USER_IDS:
        try:
            await bot.send_message(chat_id=uid, text=text, parse_mode="HTML")
            log.info("[dispatch] forwarded msg_id=%s → uid=%s", rec["message_id"], uid)
        except Exception as exc:
            log.error("[dispatch] send to uid=%s failed: %s", uid, exc)


async def _handle_worker_ant_message(application: Application, rec: dict) -> None:
    group_reply_style.capture_worker_ant_voice(
        rec.get('text') or '', msg_id=rec.get('message_id'),
    )
    if await group_roll_call_handler.try_roll_call_reply_for_record(application, rec):
        _append_inbox(rec)
        return

    if await group_workbook_progress_handler.try_workbook_progress_reply(application, rec):
        _append_inbox(rec)
        log.info('[dispatch] workbook progress posted msg_id=%s', rec.get('message_id'))
        return

    _append_inbox(rec)
    preview = (rec["text"] or "")[:120].replace("\n", " ")
    log.info("[dispatch] 工作狂人 msg_id=%s %s", rec["message_id"], preview)

    prov = register_task(
        source='worker_ant_group',
        text=rec.get('text') or '',
        uid=0,
        chat_id=rec.get('chat_id'),
        msg_id=rec.get('message_id'),
        meta={'sender': WORKER_ANT_BOT},
    )

    learn_result = None
    if WORKER_ANT_LEARN_ENABLED:
        try:
            learn_result = await learn_from_record(rec, source='worker_ant_group')
            if (AGENT_BUS_INCOMING_ONLY or AGENT_BUS_STATUS_MIRROR) and learn_result and not learn_result.get('skipped'):
                lids = learn_result.get('lesson_ids') or []
                log.info(
                    "[dispatch] silent learn group msg_id=%s lessons=%s",
                    rec["message_id"],
                    lids[:5],
                )
        except Exception as exc:
            log.error("[dispatch] learn failed msg_id=%s: %s", rec["message_id"], exc)

    summary = (learn_result or {}).get('summary') or (
        '已通知又初' if not AGENT_BUS_INCOMING_ONLY else 'incoming_only'
    )
    complete_task(prov['id'], 'completed', summary[:500])
    await _notify_assignees(application, rec, prov, learn_result)


async def _serve_chat_history_requests(client) -> None:
    """学习脚本写请求文件，这里用当前这条 session 把每个群和每条私聊的历史拉全。"""
    import group_message_capture

    last_nonce = None
    while True:
        try:
            path = group_message_capture.REQUEST_PATH
            if os.path.isfile(path):
                with open(path, encoding='utf-8') as f:
                    req = json.load(f)
                nonce = req.get('nonce')
                day = (req.get('day') or '').strip()
                if nonce and day and nonce != last_nonce:
                    last_nonce = nonce
                    log.info('[group-capture] 开始回拉群和私聊 day=%s', day)
                    try:
                        result = await group_message_capture.backfill_day(client, day)
                        result['ok'] = True
                    except Exception as exc:
                        log.exception('[group-capture] 回拉失败')
                        result = {'ok': False, 'error': str(exc), 'day': day}
                    result['nonce'] = nonce
                    group_message_capture.write_done(result)
                    log.info(
                        '[group-capture] 回拉结束 day=%s groups=%s privates=%s scanned=%s written=%s ok=%s',
                        day,
                        result.get('groups'),
                        result.get('privates'),
                        result.get('scanned'),
                        result.get('written'),
                        result.get('ok'),
                    )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning('[group-capture] 请求循环 %s', exc)
        await asyncio.sleep(2)


async def start_dispatch_watcher(application: Application) -> None:
    """在 bot 启动时挂上；未配置 Telethon 时静默跳过。"""
    if not telethon_watcher_should_start():
        if WORKER_ANT_DISPATCH_ENABLED or ATTENDANCE_CHECK_ENABLED:
            log.warning(
                "[telethon] 未启动：需 TELEGRAM_API_ID/HASH + login_user_session.py"
            )
        else:
            log.info("[telethon] dispatch/attendance 均未启用，跳过")
        return

    asyncio.create_task(_dispatch_watcher_loop(application))
    if dispatch_watcher_ready():
        log.info(
            "[dispatch] 将监听群 %s 的 @%s → 通知 %s（学习=%s）",
            MONITOR_GROUP_CHAT_ID,
            WORKER_ANT_BOT,
            TASK_DISPATCH_NOTIFY_USER_IDS,
            WORKER_ANT_LEARN_ENABLED,
        )
    if ATTENDANCE_CHECK_ENABLED:
        log.info(
            "[attendance] 将监听群 %s，被 @%s 且随机抽查时自动答题",
            ATTENDANCE_CHECK_CHAT_ID,
            ATTENDANCE_CHECK_USERNAME,
        )
    if TG_VISIBLE_ONLINE_ENABLED:
        log.info("[visible-online] 将在 dispatch Telethon 上间歇刷绿点（不断 TCP）")


async def _dispatch_watcher_loop(application: Application) -> None:
    global _telethon_client
    try:
        from telethon import TelegramClient, events
    except ImportError:
        log.error("[dispatch] 请安装 telethon: pip install telethon PySocks")
        return

    client = TelegramClient(
        USER_SESSION_PATH,
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH,
        **_client_kwargs(),
    )
    _telethon_client = client

    backfill_task = None
    try:
        await client.start()
        import group_message_capture

        @client.on(events.NewMessage())
        async def on_capture_message(event):
            try:
                group_message_capture.append_event(event)
            except Exception as exc:
                log.warning('[group-capture] %s', exc)

        backfill_task = asyncio.create_task(_serve_chat_history_requests(client))
        me = await client.get_me()
        log.info(
            "[telethon] 已连接 user=%s (@%s id=%s)",
            me.first_name,
            getattr(me, 'username', '') or '',
            me.id,
        )

        if dispatch_watcher_ready():
            worker = await client.get_entity(WORKER_ANT_BOT)
            group = await client.get_entity(MONITOR_GROUP_CHAT_ID)
            worker_id = worker.id
            log.info("[dispatch] worker_id=%s monitor_group=%s", worker_id, MONITOR_GROUP_CHAT_ID)

            @client.on(events.NewMessage(chats=group))
            async def on_worker_ant_message(event):
                rec = _record_from_event(event, worker_id)
                if not rec:
                    return
                asyncio.create_task(_handle_worker_ant_message(application, rec))

        if ATTENDANCE_CHECK_ENABLED:
            attendance_group = await client.get_entity(ATTENDANCE_CHECK_CHAT_ID)
            log.info("[attendance] watching chat_id=%s", ATTENDANCE_CHECK_CHAT_ID)

            @client.on(events.NewMessage(chats=attendance_group))
            async def on_attendance_check(event):
                try:
                    await attendance_check_handler.try_reply_attendance_check(event, client)
                except Exception as exc:
                    log.error('[attendance] handler error: %s', exc)

        if TG_VISIBLE_ONLINE_ENABLED:
            asyncio.create_task(tg_visible_online.visible_online_loop(client))

        await client.run_until_disconnected()
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        log.exception("[dispatch] watcher 异常退出: %s", exc)
    finally:
        if backfill_task is not None:
            backfill_task.cancel()
        if client.is_connected():
            await client.disconnect()
        _telethon_client = None
