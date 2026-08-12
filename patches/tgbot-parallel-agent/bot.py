#!/usr/bin/env python3
"""TGBot — Telegram + Claude for datacenter project."""
import asyncio
import os
import re
import subprocess
import time
import logging
import threading
from telegram.error import BadRequest, TimedOut
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatType
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes,
    CallbackQueryHandler,
)

import db
import ai_client
import prompt_builder
import query_queue
import work_intent
import heartbeat_handler
import casual_greeting_handler
import group_roll_call_handler
import group_workbook_progress_handler
import bot_health
import work_memory
import context_bridge
import model_quota
from worker_ant_dispatch_watcher import start_dispatch_watcher
from agent_bus_watcher import start_agent_bus_watcher
from workbook_trigger_watcher import start_workbook_watcher
from jike_checkin_watcher import start_jike_checkin_scheduler
from worker_ant_learner import backfill_unprocessed
from bot_watchdog import self_check_loop, heartbeat_loop
import direct_commands
import task_provenance
from message_style import format_bot_reply, format_group_reply, format_outgoing_block, task_ack
import group_reply_style
import tg_task_tracker
from config import (
    TG_BOT_TOKEN,
    ALLOWED_USERS,
    GROUP_ALLOWED_USERS,
    ALLOWED_GROUP_CHAT_IDS,
    GROUP_LISTEN_WITHOUT_MENTION,
    GROUP_OBSERVE_ALL,
    GROUP_REPLY_MENTIONS,
    GROUP_REPLY_MENTION_USER_IDS,
    PROJECT_ROOT,
    INCOMING_DIR,
    OUTGOING_DIR,
    CSV_INLINE_THRESHOLD_ROWS,
    SLOW_NUDGE_SEC,
    WORKER_ANT_LEARN_ENABLED,
    WORKER_ANT_UPGRADE_ENABLED,
    AGENT_BUS_STATUS_MIRROR,
)

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

# ── Auth ──

def check_auth(user_id: int) -> bool:
    if user_id in ALLOWED_USERS:
        return True
    return db.is_authorized(user_id)


def check_group_auth(user_id: int) -> bool:
    """白名单群内任意成员可 @ 机器人派活（不按用户 ID 再拦）。"""
    if GROUP_ALLOWED_USERS:
        if user_id in GROUP_ALLOWED_USERS:
            return True
        return db.is_authorized(user_id)
    return True


def _is_group_chat(update: Update) -> bool:
    chat = update.effective_chat
    return bool(chat and chat.type in (ChatType.GROUP, ChatType.SUPERGROUP))


def _group_chat_allowed(update: Update) -> bool:
    if not ALLOWED_GROUP_CHAT_IDS:
        return True
    chat = update.effective_chat
    return bool(chat and chat.id in ALLOWED_GROUP_CHAT_IDS)


def _bot_was_addressed(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """私聊一律处理；群聊 @本机器人 / @主人 / @tgbot 等触发词时处理。"""
    if not _is_group_chat(update):
        return True
    if GROUP_LISTEN_WITHOUT_MENTION:
        return True
    msg = update.message or update.effective_message
    if not msg:
        return False
    bot_id = ctx.bot.id
    bot_username = (ctx.bot.username or "").lower()
    text = msg.text or msg.caption or ""
    extra_mentions = set(GROUP_REPLY_MENTIONS)
    owner_ids = set(GROUP_REPLY_MENTION_USER_IDS)

    for ent in msg.entities or []:
        if ent.type == "mention" and text:
            seg = text[ent.offset: ent.offset + ent.length].lower().lstrip('@')
            if bot_username and seg == bot_username:
                return True
            if seg in extra_mentions:
                return True
        if ent.type == "text_mention" and ent.user:
            if ent.user.id == bot_id:
                return True
            if ent.user.id in owner_ids:
                return True
    if text:
        for name in extra_mentions:
            if re.search(rf'@{re.escape(name)}\b', text, re.I):
                return True
    return False


def _is_reply_to_bot(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    msg = update.message or update.effective_message
    if not msg or not msg.reply_to_message:
        return False
    r = msg.reply_to_message
    return bool(r.from_user and r.from_user.id == ctx.bot.id)


def _group_signal_text(update: Update, body: str) -> str:
    user = update.effective_user
    uname = (user.username or user.first_name or str(user.id)).strip()
    return f"[群聊·@{uname}]: {(body or '').strip()}"


def _strip_bot_mention(text: str, bot_username: str | None) -> str:
    if not text:
        return text
    out = text
    names: set[str] = set(GROUP_REPLY_MENTIONS)
    if bot_username:
        names.add(bot_username.lower())
    for name in sorted(names, key=len, reverse=True):
        out = re.sub(rf'@{re.escape(name)}\s*', '', out, flags=re.IGNORECASE)
    return out.strip()


def _mention_prefix(update: Update) -> str | None:
    """群聊回复首行 @提问者；私聊不加前缀。"""
    if not _is_group_chat(update):
        return None
    user = update.effective_user
    if user.username:
        return f"@{user.username}"
    return (user.first_name or "用户").strip() or "用户"


def _user_reply_text(update: Update, body: str) -> str:
    """@提问者 + 换行 + 正文（群聊）。"""
    prefix = _mention_prefix(update)
    if not prefix:
        return body
    return f"{prefix}\n{body}"


async def _send_user_message(update: Update, body: str, **kwargs):
    """新发一条消息；群聊首行 @提问者，不引用原消息。"""
    bot = kwargs.pop('bot', None) or update.get_bot()
    return await _send_chat_message(
        update.effective_chat.id,
        body,
        mention_prefix=_mention_prefix(update),
        bot=bot,
        **kwargs,
    )


async def _send_chat_message(
    chat_id: int,
    body: str,
    *,
    mention_prefix: str | None = None,
    bot=None,
    **kwargs,
):
    """统一出站：@提问者（可选）+ 新发消息，永不 reply_to。"""
    kwargs.pop('reply_to_message_id', None)
    if mention_prefix:
        text = f"{mention_prefix}\n{body}"
    else:
        text = body
    sender = bot or (_bot_app.bot if _bot_app else None)
    if sender is None:
        raise RuntimeError('bot not available for send_message')
    return await sender.send_message(
        chat_id=chat_id,
        text=text[:4096],
        **kwargs,
    )


async def _reply_user(update: Update, body: str, **kwargs):
    return await _send_user_message(update, body, **kwargs)


async def _send_job_message(job, body: str, **kwargs):
    """SQL 队列等无 Update 场景：新发消息 @提问者。"""
    parts = split_message(body)
    last = None
    for i, part in enumerate(parts):
        last = await _send_chat_message(
            job.meta.get('tg_chat_id') or job.chat_id,
            part,
            mention_prefix=job.meta.get('mention_prefix') if i == 0 else None,
            **kwargs if i == 0 else {k: v for k, v in kwargs.items() if k != 'reply_markup'},
        )
    return last


async def _edit_user_reply(update: Update, msg, body: str):
    """已弃用：统一改为新发消息，保留兼容旧调用。"""
    await _send_user_message(update, body)


# ── Helpers ──

def ensure_session(user_id: int) -> dict:
    """私聊/群聊均走 workspace 共用会话。"""
    return db.ensure_workspace_session()


def _format_agent_message(update: Update, text: str) -> str:
    """群聊消息带上发言人，写入共用对话历史。"""
    if not _is_group_chat(update):
        return text
    user = update.effective_user
    who = f"@{user.username}" if user and user.username else (
        (user.first_name if user else None) or str(user.id if user else '?')
    )
    return f"[群聊·{who}]: {text}"

def split_message(text: str, max_len=4000) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        split_at = text.rfind('\n', 0, max_len)
        if split_at <= 0:
            split_at = max_len
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()
    return parts

async def _safe_edit(msg, text: str):
    try:
        await msg.edit_text(text[:4096])
    except (BadRequest, TimedOut):
        pass

# ── Commands ──

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """与「帮助」/「?」/「？」走同一条路径，按角色区分内容"""
    uid = update.effective_user.id
    if not check_auth(uid):
        log.warning("Unauthorized /start|help uid=%s allowed=%s", uid, ALLOWED_USERS)
        await _send_user_message(
            update,
            f"⛔ 未授权\n你的 Telegram ID：{uid}\n请把此数字发给管理员加入授权。",
        )
        return
    await _send_user_help(update, uid)

async def cmd_new(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    old = db.get_workspace_session()
    if old and old.get('id'):
        conn = db.get_db()
        conn.execute("UPDATE sessions SET status='closed' WHERE id=?", (old['id'],))
        conn.commit()
    session = db.ensure_workspace_session()
    db.set_user_state(uid, session['id'])
    await _send_user_message(update, "🆕 新会话已开始（已清空共用 Cursor 上下文）")

async def cmd_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    tasks = db.get_tasks()
    if not tasks:
        await _send_user_message(update,"暂无任务。")
        return
    icons = {'completed': '✅', 'in_progress': '⏳', 'pending': '📋', 'failed': '❌'}
    lines = [f"{icons.get(t['status'], '•')} {t['title']}" for t in tasks[:15]]
    await _send_user_message(update,"📋 *任务*\n\n" + '\n'.join(lines), parse_mode='Markdown')

async def cmd_rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    pub = db.get_public_rules()
    mine = db.get_user_rules(uid)
    if not pub and not mine:
        await _send_user_message(update,"暂无规则。/addrule 添加自己的；公共规则需控制台 cli.py rule add。")
        return
    sections = []
    if pub:
        lines = [f"#{r['id']}  `{r['table_pattern']}` — {r['rule']}" for r in pub]
        sections.append("🌐 *公共规则*（所有用户共享）\n" + '\n'.join(lines))
    if mine:
        lines = [f"#{r['id']}  `{r['table_pattern']}` — {r['rule']}" for r in mine]
        sections.append(f"👤 *我的规则*（uid={uid}）\n" + '\n'.join(lines))
    await _send_user_message(update,'\n\n'.join(sections), parse_mode='Markdown')

async def cmd_addrule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    text = update.message.text.replace('/addrule', '', 1).strip()
    parts = text.split(' ', 1)
    if len(parts) < 2:
        await _send_user_message(update,
            "用法: /addrule <表名模式> <规则描述>\n"
            "例: /addrule dwd_order_paid_d 金额单位是分，÷100 换元\n\n"
            "管理员添加时会问你存私有还是公共"
        )
        return
    table, rule = parts[0], parts[1]
    if db.is_superuser(uid):
        await _admin_choose_scope(
            update, kind='rule',
            payload={'table_pattern': table, 'rule': rule},
            description=f"📏 表 `{table}` — {rule}",
        )
    else:
        rid = db.add_query_rule(table, rule, owner_user_id=uid)
        await _send_user_message(update,f"✅ 私有规则 #{rid} 已添加：`{table}` — {rule}", parse_mode='Markdown')


async def cmd_delrule(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    args = ctx.args or []
    if not args or not args[0].isdigit():
        await _send_user_message(update,"用法: /delrule <id>\n只能删自己的规则；公共规则要去控制台删。")
        return
    rid = int(args[0])
    if db.is_superuser(uid):
        n = db.delete_query_rule(rid)
    else:
        n = db.delete_query_rule(rid, owner_user_id=uid)
    if n:
        await _send_user_message(update,f"🗑 规则 #{rid} 已删除")
    else:
        await _send_user_message(update,f"⚠️ 没有这条规则，或不属于你（uid={uid}）")


async def cmd_aliases(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    rows = db.get_user_aliases(uid)
    if not rows:
        await _send_user_message(update,
            "你还没有私有别名。\n"
            "用 /addalias <别名> <目标> 添加；公共别名维护在 omdb/.claude/database/aliases.md。"
        )
        return
    lines = [f"#{r['id']}  {r['alias']} => `{r['target']}`" for r in rows]
    await _send_user_message(update,
        f"👤 *我的私有别名*（uid={uid}）\n" + '\n'.join(lines),
        parse_mode='Markdown',
    )


async def cmd_addalias(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    text = update.message.text.replace('/addalias', '', 1).strip()
    parts = text.split(' ', 1)
    if len(parts) < 2:
        await _send_user_message(update,
            "用法: /addalias <业务别名> <真实目标>\n"
            "例: /addalias 我的订单表 dwd.dwd_order_paid_d\n\n"
            "管理员添加时会问你存私有还是公共"
        )
        return
    alias, target = parts[0], parts[1]
    if db.is_superuser(uid):
        await _admin_choose_scope(
            update, kind='alias',
            payload={'alias': alias, 'target': target},
            description=f"🏷 {alias} => `{target}`",
        )
    else:
        aid = db.add_user_alias(uid, alias, target)
        await _send_user_message(update,f"✅ 私有别名 #{aid} 已添加：{alias} => `{target}`", parse_mode='Markdown')


async def cmd_delalias(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    args = ctx.args or []
    if not args or not args[0].isdigit():
        await _send_user_message(update,"用法: /delalias <id>\n只能删自己的别名。")
        return
    aid = int(args[0])
    n = db.delete_user_alias(aid, owner_user_id=uid if not db.is_superuser(uid) else None)
    if n:
        await _send_user_message(update,f"🗑 别名 #{aid} 已删除")
    else:
        await _send_user_message(update,f"⚠️ 没有这条别名，或不属于你")


async def cmd_teach(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """显式教 bot 一条规则：/teach <scope> | <rule>  或  /teach <rule>（无 scope）"""
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    raw = update.message.text.replace('/teach', '', 1).strip()
    if not raw:
        await _send_user_message(update,
            "用法：/teach <范围> | <规则>\n"
            "   或：/teach <规则>（不带范围）\n\n"
            "例：\n"
            "  /teach 订单查询 | 默认按用户的注册渠道分组\n"
            "  /teach 看个数就给个数，不要主动按 app 拆\n\n"
            "管理员添加时会问你存私有还是公共"
        )
        return
    if '|' in raw:
        scope, lesson = raw.split('|', 1)
        scope, lesson = scope.strip(), lesson.strip()
    else:
        scope, lesson = "", raw
    if not lesson:
        await _send_user_message(update,"规则文本不能空")
        return
    if db.is_superuser(uid):
        await _admin_choose_scope(
            update, kind='lesson',
            payload={'scope': scope, 'lesson': lesson},
            description=f"📚 [{scope or '通用'}] {lesson}",
        )
    else:
        lid = db.add_lesson(
            owner_user_id=uid, source='manual', scope=scope, lesson=lesson,
            related_question=None,
        )
        await _send_user_message(update,
            f"✅ 已记 lesson #{lid}\n"
            f"   范围：{scope or '(无)'}\n"
            f"   规则：{lesson}\n"
            f"   仅你私有；可用 /lessons 查、/lessons del {lid} 删"
        )


async def cmd_grant(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """管理员授权用户：/grant <user_id> [admin|operator]"""
    uid = update.effective_user.id
    if not (check_auth(uid) and db.is_superuser(uid)):
        await _send_user_message(update,"⛔ 仅管理员可操作")
        return
    args = ctx.args or []
    if not args or not args[0].lstrip('-').isdigit():
        await _send_user_message(update,
            "用法: /grant <user_id> [admin|operator]\n"
            "默认 operator；admin 拥有管理员权限"
        )
        return
    target = int(args[0])
    role = args[1] if len(args) > 1 else 'operator'
    if role not in ('admin', 'operator'):
        await _send_user_message(update,"⚠️ role 只能是 admin 或 operator")
        return
    db.authorize(target, role)
    await _send_user_message(update,f"✅ 用户 {target} 已授权（{role}）")


async def cmd_revoke(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """管理员撤销用户：/revoke <user_id>"""
    uid = update.effective_user.id
    if not (check_auth(uid) and db.is_superuser(uid)):
        await _send_user_message(update,"⛔ 仅管理员可操作")
        return
    args = ctx.args or []
    if not args or not args[0].lstrip('-').isdigit():
        await _send_user_message(update,"用法: /revoke <user_id>")
        return
    target = int(args[0])
    if target == uid:
        await _send_user_message(update,"⚠️ 不能撤销自己")
        return
    conn = db.get_db()
    cur = conn.execute("DELETE FROM authorizations WHERE telegram_user_id=?", (target,))
    conn.commit()
    if cur.rowcount:
        await _send_user_message(update,f"🗑 用户 {target} 已撤销授权")
    else:
        await _send_user_message(update,f"⚠️ 用户 {target} 本来就没授权")


async def cmd_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """管理员重启 bot：/restart。会断开当前 polling，重新拉起。"""
    uid = update.effective_user.id
    if not (check_auth(uid) and db.is_superuser(uid)):
        await _send_user_message(update,"⛔ 仅管理员可操作")
        return
    await _send_user_message(update,
        "🔄 正在重启 bot...\n"
        "（如果 30 秒后没收到 \"启动完成\" 提示，请到服务器手动跑 omdb/tgbot/restart.sh）"
    )
    restart_sh = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restart.sh')
    try:
        # 脱离当前进程组，restart.sh 会先 kill 当前进程再起新的
        subprocess.Popen(
            ['bash', restart_sh],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        await _send_user_message(update,f"❌ 重启失败：{e}")


async def cmd_lessons(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查 / 删 / 升级 lessons:
       /lessons              # 列我的 + 公共
       /lessons del <id>     # 删自己的（admin 可删任意）
       /lessons promote <id> # admin 把私有升级为公共
    """
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    args = ctx.args or []
    if args and args[0] == 'del' and len(args) >= 2 and args[1].isdigit():
        lid = int(args[1])
        if db.is_superuser(uid):
            n = db.delete_lesson(lid)
        else:
            n = db.delete_lesson(lid, owner_user_id=uid)
        await _send_user_message(update,
            f"🗑 lesson #{lid} 已归档" if n else f"⚠️ 没这条或不属于你"
        )
        return
    if args and args[0] == 'promote' and len(args) >= 2 and args[1].isdigit():
        if not db.is_superuser(uid):
            await _send_user_message(update,"⚠️ 仅管理员可升级公共")
            return
        lid = int(args[1])
        n = db.promote_lesson(lid)
        await _send_user_message(update,
            f"🌐 lesson #{lid} 已升公共" if n else f"⚠️ 没这条 lesson"
        )
        return

    pub = db.get_public_lessons()
    mine = db.get_user_lessons(uid)
    if not pub and not mine:
        await _send_user_message(update,
            "暂无 lessons。\n"
            "  - 用 /teach <范围> | <规则> 手动加\n"
            "  - 或者跟 bot 说 \"以后...\" / \"记住...\" 让它自动检测并问你存不存"
        )
        return
    sections = []
    if pub:
        lines = [f"#{r['id']}  [{r.get('scope') or '通用'}] {r['lesson']}" for r in pub]
        sections.append("🌐 *公共 lessons*\n" + '\n'.join(lines))
    if mine:
        lines = [f"#{r['id']}  [{r.get('scope') or '通用'}] {r['lesson']}  (来源:{r['source']})" for r in mine]
        sections.append(f"👤 *我的 lessons* (uid={uid})\n" + '\n'.join(lines))
    await _send_user_message(update,'\n\n'.join(sections), parse_mode='Markdown')

async def cmd_reminders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    reminders = db.get_user_reminders(uid)
    if not reminders:
        await _send_user_message(update,"没有待执行的提醒。")
        return
    lines = [f"⏰ {r['remind_at']} — {r['message']}" for r in reminders]
    await _send_user_message(update,"📋 *待执行提醒*\n\n" + '\n'.join(lines), parse_mode='Markdown')

async def cmd_sendfile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    args = ' '.join(ctx.args) if ctx.args else ''
    if not args:
        await _send_user_message(update,"用法: /sendfile <路径>")
        return

    sandbox = db.get_user_sandbox(uid)
    candidates = [os.path.join(PROJECT_ROOT, args), os.path.join(sandbox, args), args]
    fpath = None
    for c in candidates:
        if os.path.isfile(c):
            fpath = c
            break
    if not fpath:
        await _send_user_message(update,f"文件不存在: {args}")
        return

    # Non-superuser can only send from sandbox + project
    if not db.is_superuser(uid):
        real = os.path.realpath(fpath)
        if not (real.startswith(os.path.realpath(sandbox)) or real.startswith(os.path.realpath(PROJECT_ROOT))):
            await _send_user_message(update,"⛔ 无权限访问该文件")
            return

    size = os.path.getsize(fpath)
    if size > 50 * 1024 * 1024:
        await _send_user_message(update,f"文件太大 ({size // 1024 // 1024}MB)")
        return
    await update.get_bot().send_document(
        chat_id=update.effective_chat.id,
        document=open(fpath, 'rb'),
        filename=os.path.basename(fpath),
    )

# ── File receive ──

async def handle_file(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _bot_was_addressed(update, ctx):
        return
    if _is_group_chat(update) and not _group_chat_allowed(update):
        return
    uid = update.effective_user.id
    if _is_group_chat(update):
        if not check_group_auth(uid):
            return
    elif not check_auth(uid):
        return
    doc = update.message.document
    if not doc:
        return
    save_path = os.path.join(INCOMING_DIR, doc.file_name or f'file_{int(time.time())}')
    file = await ctx.bot.get_file(doc.file_id)
    await file.download_to_drive(save_path)
    caption = update.message.caption or ""
    await _send_user_message(update,f"📎 文件已保存: `{save_path}`", parse_mode='Markdown')
    if caption:
        synthetic = f"用户发送了文件 {save_path}（文件名: {doc.file_name}），并说: {caption}"
        await handle_message(update, ctx, message_text=synthetic)

# ── Natural language ──

# 全渠道 Agent 串行队列（私聊 + 群聊共用 cursor 会话，必须单线程）
_AGENT_QUEUE_KEY = 0
_user_serial = {}  # key -> {'lock': Lock, 'waiters': [...]}


async def _wait_my_turn(
    update: Update, uid: int, user_text: str = "", ack_msg=None,
) -> dict | None:
    """如果当前用户已有消息在处理，返回一个 ack message 让 ticker 显示位置。
    返回 dict 包含 wait_msg / event / submit_at / user_text / user_msg_id。"""
    state = _user_serial.setdefault(uid, {'lock': asyncio.Lock(), 'waiters': []})
    waiters = state['waiters']
    if not user_text:
        user_text = update.message.text or ""
    me = {
        'event': asyncio.Event(),
        'wait_msg': None,
        'submit_at': time.time(),
        'user_text': user_text,
        'user_msg_id': update.message.message_id,
        'mention_prefix': _mention_prefix(update),
    }
    pos = len(waiters)
    waiters.append(me)
    if pos > 0 and not _is_group_chat(update):
        try:
            me['wait_msg'] = await _reply_user(update, f"前面还有 {pos} 条在处理")
        except Exception as e:
            log.warning(f"[serial] queue ack failed: {e}")
    elif ack_msg:
        me['wait_msg'] = ack_msg
    return me


async def _release_my_turn(uid: int, me: dict):
    state = _user_serial.get(uid)
    if not state:
        return
    waiters = state['waiters']
    if me in waiters:
        waiters.remove(me)


_HELP_KEYWORDS = {"帮助", "?", "？", "help", "Help"}


def _user_help_text(is_admin: bool) -> str:
    base = (
        "👋 *我能帮你做什么*\n\n"
        "📊 *直接发问做数据查询*（多个人发问会自动排队）\n"
        "  • \"5月2日充值多少钱\"\n"
        "  • \"昨天注册前 10 个 app，要文件\"\n"
        "  • \"查一下 X 表都有什么字段\"\n"
        "  • 答完会问你 👍/👎；你 👎 我会反思学一条规则\n\n"
        "📚 *管理你的规则 / 别名 / 经验（都是私有）*\n"
        "  • `/rules` 看规则；`/addrule <表> <规则>` 加；`/delrule <id>` 删\n"
        "  • `/aliases` 看别名；`/addalias <别名> <目标>` 加；`/delalias <id>` 删\n"
        "  • `/lessons` 看学到的；`/teach <范围> | <规则>` 教我一条\n\n"
        "🛠 *其他*\n"
        "  • `/new` 新会话；`/tasks` 任务列表；`/queue` 看 SQL 队列\n"
        "  • `/askant <问题>` 经 agent-bus 转问工作狂人\n"
        "  • `回复 工作狂人：<内容>` 经 agent-bus 秒发（不经 AI）\n"
        "  • `问 工作狂人：<问题>` 经 agent-bus 转问（不经 AI）\n"
        "  • 其他问题直接 @ 我，走 AI 回答（不会自动转问狂人）\n"
        "  • `/reminders` 待执行提醒\n"
        "  • 直接给我发文件，我会收到\n\n"
        "💡 *小贴士*\n"
        "  • 想学到一条规则：跟我说 \"以后...\" / \"记住...\" / \"不对，应该...\"，我会主动建议存\n"
        "  • 大表查询会自动加 LIMIT 兜底；金额字段单位是分，我会自动 ÷100 换元"
    )
    if is_admin:
        base += (
            "\n\n👑 *管理员专属*\n"
            "  • `/grant <user_id> [admin|operator]` 授权用户\n"
            "  • `/revoke <user_id>` 撤销授权\n"
            "  • `/restart` 重启 bot\n"
            "  • `/addrule` / `/addalias` / `/teach` 你来用会**问你存私有还是公共**\n"
            "  • `/lessons promote <id>` 把私有规则升公共"
        )
    return base


async def _send_user_help(update: Update, uid: int):
    is_admin = db.is_superuser(uid)
    await _reply_user(
        update,
        _user_help_text(is_admin),
        parse_mode='Markdown',
    )


async def handle_message(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE, *, message_text: str | None = None,
):
    in_group = _is_group_chat(update)
    if in_group and not _group_chat_allowed(update):
        return

    mentioned = _bot_was_addressed(update, ctx)

    uid = update.effective_user.id
    raw_text = message_text if message_text is not None else (update.message.text or "")
    cleaned = _strip_bot_mention(raw_text, ctx.bot.username) if in_group else raw_text.strip()

    if in_group and GROUP_OBSERVE_ALL:
        if check_group_auth(uid):
            context_bridge.append_signal(
                text=_group_signal_text(update, cleaned or raw_text),
                source='telegram_group',
                author=_mention_prefix(update),
                uid=uid,
                meta={
                    'chat_id': update.effective_chat.id,
                    'msg_id': update.message.message_id,
                },
            )
        # 群旁听写入 context；@本 bot / @主人 / @tgbot 才回复
        # 例外：知秋/狂人点名在吗/谁活着/机器人挂了 → 健康则秒回（不拉 Agent）
        if not mentioned:
            async def _roll_reply(body: str) -> None:
                await _reply_user(update, body)

            if await group_roll_call_handler.try_proactive_roll_call_reply(
                update, text=cleaned or raw_text, reply_fn=_roll_reply,
            ):
                return
            if await group_workbook_progress_handler.try_proactive_workbook_reply(
                update,
                text=cleaned or raw_text,
                reply_fn=_roll_reply,
                application=_bot_app,
            ):
                return
            return
    elif not mentioned:
        return

    if in_group:
        if not check_group_auth(uid):
            log.warning("Unauthorized group message uid=%s", uid)
            await _reply_user(
                update,
                f"⛔ 群聊未授权\n你的 Telegram ID：{uid}\n请联系管理员 /grant。",
            )
            return
    elif not check_auth(uid):
        log.warning("Unauthorized message uid=%s allowed=%s", uid, ALLOWED_USERS)
        await _reply_user(
            update,
            f"⛔ 未授权\n你的 Telegram ID：{uid}\n请把此数字发给管理员加入授权。",
        )
        return

    msg_stripped = cleaned.strip()
    if msg_stripped in _HELP_KEYWORDS:
        await _send_user_help(update, uid)
        return

    source = task_provenance.chat_source(in_group=in_group)
    cmd = direct_commands.parse(cleaned)
    if cmd:
        task_rec = task_provenance.register_task(
            source=source,
            text=cleaned,
            uid=uid,
            chat_id=update.effective_chat.id,
            msg_id=update.message.message_id,
        )
        try:
            if cmd.kind in ('ask_ant', 'reply_ant'):
                ack_text = task_ack(kind=cmd.kind, in_group=in_group)
                if not AGENT_BUS_STATUS_MIRROR:
                    await _reply_user(update, ack_text)
                if AGENT_BUS_STATUS_MIRROR and _bot_app:
                    await tg_task_tracker.notify_incoming(
                        _bot_app,
                        channel=source,
                        task_label=task_rec['label'],
                        body=cleaned,
                    )
            result = await direct_commands.execute(
                cmd, source=source, uid=uid, task_rec=task_rec,
            )
            for part in split_message(result):
                await _send_user_message(update, part)
            if AGENT_BUS_STATUS_MIRROR:
                tg_task_tracker.emit_reply(
                    task_rec['label'], channel=source, text=result[:3500],
                )
        except Exception as exc:
            task_provenance.complete_task(task_rec['id'], 'failed', str(exc))
            if AGENT_BUS_STATUS_MIRROR:
                tg_task_tracker.emit_reply(
                    task_rec['label'], channel=source, text=f'执行失败: {exc}',
                )
            await _reply_user(update, f"❌ 执行失败: {exc}")
        return

    if work_intent.is_heartbeat(cleaned):
        reply = await heartbeat_handler.build_reply(cleaned)
        await _reply_user(update, reply)
        return

    if work_intent.is_casual_greeting(cleaned):
        reply = await casual_greeting_handler.build_reply(cleaned)
        await _reply_user(update, reply)
        return

    if work_intent.is_simple_preference(cleaned):
        lesson = (
            '用户称呼「初儿」即指又初（数据中心开发助手），与「又初」等价。'
            if '初儿' in cleaned else cleaned.strip()
        )
        lid = db.add_lesson(
            owner_user_id=uid,
            source='user_teach',
            scope='称呼',
            lesson=lesson,
            related_question=cleaned[:200],
        )
        context_bridge.append_exchange(
            uid=uid,
            question=cleaned,
            answer=work_intent.preference_reply(cleaned),
            source=source,
            author=_mention_prefix(update),
        )
        await _reply_user(
            update,
            f"{work_intent.preference_reply(cleaned)}\n（已记入 lesson #{lid}）",
        )
        return

    if not work_intent.is_work_request(cleaned):
        reply = work_intent.casual_reply(cleaned)
        await _reply_user(update, reply)
        return

    prov_task = task_provenance.register_task(
        source=source,
        text=cleaned,
        uid=uid,
        chat_id=update.effective_chat.id,
        msg_id=update.message.message_id,
    )
    if AGENT_BUS_STATUS_MIRROR and _bot_app:
        await tg_task_tracker.notify_incoming(
            _bot_app,
            channel=source,
            task_label=prov_task['label'],
            body=cleaned,
            extra_lines=[_mention_prefix(update)] if in_group else None,
        )

    ack_text = task_ack(kind='work', in_group=in_group, user_text=cleaned)
    ack_msg = None
    if in_group:
        ack_msg = await _group_work_instant_ack(update, text=cleaned)
    elif not AGENT_BUS_STATUS_MIRROR:
        ack_msg = await _reply_user(update, ack_text)

    from agent_queue import should_spawn_parallel_for_dm

    # 私聊叠单：长活占着 → 另开 agent（不进「前面还有 N 条」队列，不 resume）
    if (not in_group) and should_spawn_parallel_for_dm():
        try:
            await _reply_user(
                update,
                "当前有任务在跑，另开 agent 处理本条（会读记忆冷启动）。",
            )
        except Exception as e:
            log.warning('[parallel] notify failed: %s', e)
        await _handle_message_core(
            update, ctx, message_text=cleaned, status_msg=ack_msg,
            prov_task=prov_task,
            force_new_agent=True,
            parallel=True,
        )
        return

    me = await _wait_my_turn(update, _AGENT_QUEUE_KEY, user_text=cleaned, ack_msg=ack_msg)
    state = _user_serial[_AGENT_QUEUE_KEY]
    async with state['lock']:
        try:
            if me and me.get('wait_msg') and me['wait_msg'] is not ack_msg:
                try:
                    await me['wait_msg'].delete()
                except (BadRequest, TimedOut):
                    pass
            await _handle_message_core(
                update, ctx, message_text=cleaned, status_msg=ack_msg,
                prov_task=prov_task,
            )
        finally:
            await _release_my_turn(_AGENT_QUEUE_KEY, me)


async def _group_work_instant_ack(update: Update, *, text: str = ''):
    """群聊 @派活：健康则秒回自然确认（不走 Agent），活后台干完再同步结果。"""
    report = await asyncio.to_thread(bot_health.check_health)
    if not report.healthy:
        log.warning('[group] skip instant ack unhealthy: %s', report.issues[:2])
        return None
    ack = group_reply_style.instant_group_ack(text)
    return await _reply_user(update, ack)


async def _progress_nudge_loop(update: Update, done: asyncio.Event):
    """长任务进度提醒（仅私聊）。SLOW_NUDGE_SEC<=0 时关闭，避免占满 TG。"""
    if SLOW_NUDGE_SEC <= 0 or _is_group_chat(update):
        await done.wait()
        return
    tick = 0
    while not done.is_set():
        try:
            await asyncio.wait_for(done.wait(), timeout=SLOW_NUDGE_SEC)
            return
        except asyncio.TimeoutError:
            if done.is_set():
                return
            tick += 1
            # 最多提醒 1 次，之后静默（防止「约 N 分钟」刷屏）
            if tick > 1:
                continue
            await _send_user_message(
                update, f"⏳ 还在处理中…（约 {max(1, SLOW_NUDGE_SEC // 60)} 分钟，完成后会回）",
            )


async def _handle_message_core(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE, message_text: str,
    status_msg=None,
    prov_task: dict | None = None,
    *,
    force_new_agent: bool = False,
    parallel: bool = False,
):
    uid = update.effective_user.id
    in_group = _is_group_chat(update)
    source = task_provenance.chat_source(in_group=in_group)
    if prov_task is None:
        prov_task = task_provenance.register_task(
            source=source,
            text=message_text,
            uid=uid,
            chat_id=update.effective_chat.id,
            msg_id=update.message.message_id,
        )
    label = prov_task['label']
    message = f"[{label}] " + _format_agent_message(update, message_text)
    if force_new_agent:
        message = (
            f"[新开agent·并行] {message}\n"
            "（系统：长任务占着另一路 agent；本条独立处理，须先读记忆冷启动。）"
        )
    log.info(
        f"[MSG] from={uid} chat={update.effective_chat.id} "
        f"msg_id={update.message.message_id} parallel={parallel} "
        f"new_agent={force_new_agent} text={message[:50]}"
    )

    session = ensure_session(uid)
    db.set_user_state(uid, session['id'])

    superuser = db.is_superuser(uid)
    in_group = _is_group_chat(update)
    system_prompt = prompt_builder.build_system_prompt(
        uid,
        user_question=message,
        in_group=in_group,
        force_new_agent=force_new_agent,
    )

    history = db.get_history(session['id'], limit=20)
    messages = [{"role": m['role'], "content": m['content']} for m in history]
    messages.append({"role": "user", "content": message})
    db.save_message(session['id'], 'user', message)

    task = db.create_task(session['id'], message[:100])
    # 并行新开：禁止 resume 旧 cursor chat，避免抢长活会话
    cursor_chat_id = None if force_new_agent else session.get('cursor_chat_id')
    done = asyncio.Event()
    nudge_task = asyncio.create_task(_progress_nudge_loop(update, done))

    try:
        loop = asyncio.get_event_loop()

        def on_chunk(chunk: str):
            pass

        def run_stream():
            return ai_client.chat_stream(
                system_prompt, messages,
                on_chunk=on_chunk,
                is_superuser=superuser,
                cursor_chat_id=cursor_chat_id,
                task_type='chat',
            )

        async def _locked_stream():
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, run_stream)

        from agent_queue import run_locked, run_parallel
        runner = run_parallel if parallel else run_locked
        chat_result = await runner(_locked_stream)
        result_text = model_quota.ensure_nonempty(
            (chat_result.text or '').strip(),
            task_type='chat',
            tried=[ai_client.pick_model('chat')],
        )
        # 并行新开会话的 cursor_chat_id 不写回 workspace，避免覆盖长活 resume
        if chat_result.cursor_chat_id and not force_new_agent:
            db.set_session_cursor_chat_id(session['id'], chat_result.cursor_chat_id)

        db.save_message(session['id'], 'assistant', result_text)
        db.update_task(task['id'], status='completed', result=result_text[:10000])
        task_provenance.complete_task(prov_task['id'], 'completed', result_text[:500])
        context_bridge.append_exchange(
            uid=uid,
            question=message,
            answer=result_text[:1200],
            source=source,
            author=_mention_prefix(update),
        )

        # Auto-send files
        await _send_detected_files(update, result_text, uid)

        # Parse reminders
        await _parse_reminders(update, result_text)

        # 解析 [SQL: ...] 投递到查询队列（每条 SQL ack 也带上用户原话）
        await _enqueue_sql_blocks(update, result_text, uid, task_id=task['id'], user_text=message)

        # [ASK_ANT] 已废弃：问狂人请用「问 工作狂人：」；用户问又初由 AI 直接答，此处仅剥离标记

        # 工作内容：自动沉淀 lesson + 工作索引（下次同类更快）
        lesson_ids = _auto_persist_work_lessons(uid, message, result_text)
        has_sql = bool(_SQL_RE.search(result_text))
        work_memory.append_work_record(
            uid=uid,
            question=message,
            result_summary=result_text[:800],
            task_id=prov_task['id'],
            has_sql=has_sql,
            source=source,
        )

        # Clean markers
        display_text = re.sub(r'\[SEND_FILE:\s*[^\]]+\]\s*', '', result_text)
        display_text = re.sub(r'\[REMIND:\s*[^\]]+\]\s*', '', display_text).strip()
        display_text = re.sub(r'\[(SQL|SQL_FILE):\s*.*?\]', '[SQL → 队列]', display_text, flags=re.DOTALL).strip()
        display_text = re.sub(r'\[ASK_ANT:\s*.*?\]\s*', '', display_text, flags=re.DOTALL).strip()
        display_text = re.sub(r'\[LESSON:\s*.*?\]\s*', '', display_text, flags=re.DOTALL).strip()

        reply_fmt = format_group_reply if in_group else format_bot_reply
        for part in split_message(display_text):
            await _send_user_message(update, reply_fmt(part))

        if AGENT_BUS_STATUS_MIRROR:
            tg_task_tracker.emit_reply(
                prov_task['label'], channel=source, text=display_text[:3500],
            )

    except Exception as e:
        log.error(f"Claude error: {e}")
        db.update_task(task['id'], status='failed', result=str(e))
        task_provenance.complete_task(prov_task['id'], 'failed', str(e))
        if AGENT_BUS_STATUS_MIRROR:
            tg_task_tracker.emit_reply(
                prov_task['label'], channel=source, text=f'执行失败: {e}',
            )
        await _send_user_message(update, f"❌ 执行失败: {e}")
    finally:
        done.set()
        nudge_task.cancel()

# ── File detection ──

def _detect_files(text: str, uid: int) -> list[str]:
    found = []
    sandbox = db.get_user_sandbox(uid)
    for match in re.finditer(r'\[SEND_FILE:\s*([^\]]+)\]', text):
        fpath = match.group(1).strip()
        candidates = [
            os.path.join(OUTGOING_DIR, fpath),
            os.path.join(PROJECT_ROOT, fpath),
            os.path.join(sandbox, fpath),
            fpath,
        ]
        for c in candidates:
            if os.path.isfile(c) and os.path.getsize(c) < 50 * 1024 * 1024:
                if c not in found:
                    found.append(c)
                break
    return found

async def _send_detected_files(update: Update, text: str, uid: int):
    files = _detect_files(text, uid)
    for fpath in files[:5]:
        try:
            await update.get_bot().send_document(
                chat_id=update.effective_chat.id,
                document=open(fpath, 'rb'),
                filename=os.path.basename(fpath),
                caption=f"📄 {os.path.basename(fpath)}",
            )
        except Exception as e:
            log.warning(f"[FILE] failed to send {fpath}: {e}")

# ── Lesson learning ──

# [LESSON: scope | rule]：Claude 检测到用户要教/纠正时 emit
_LESSON_RE = re.compile(r'\[LESSON:\s*(.+?)\]', re.DOTALL)

# pending lessons: token -> {uid, scope, lesson, related_question}
# 5 分钟过期
_pending_lessons: dict[str, dict] = {}


def _new_token() -> str:
    import secrets
    return secrets.token_urlsafe(8)


async def _propose_lesson(update: Update, uid: int, *, scope: str, lesson: str, related_question: str = ""):
    """把 Claude emit 的 [LESSON: ...] 转成 inline 按钮，用户确认是否存"""
    token = _new_token()
    _pending_lessons[token] = {
        'uid': uid,
        'scope': scope,
        'lesson': lesson,
        'related_question': related_question,
        'expire_at': time.time() + 300,
    }
    text = (
        f"📚 我想记住一条规则：\n\n"
        f"   • 范围：{scope or '(无具体范围)'}\n"
        f"   • 规则：{lesson}\n\n"
        f"以后查询会自动应用。要存吗？"
    )
    is_admin = db.is_superuser(uid)
    keyboard = [[
        InlineKeyboardButton("✅ 存为我私有", callback_data=f"lesson:save:{token}"),
    ]]
    if is_admin:
        keyboard[0].append(
            InlineKeyboardButton("🌐 存为公共（admin）", callback_data=f"lesson:public:{token}")
        )
    keyboard.append([InlineKeyboardButton("❌ 取消", callback_data=f"lesson:cancel:{token}")])
    try:
        await _reply_user(
            update,
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        log.warning(f"[lesson] propose failed: {e}")


def _parse_lesson_marker(raw: str) -> tuple[str, str] | None:
    """[LESSON: scope | rule] 内容用 '|' 分两段；没有 '|' 视为整段都是 rule，scope 空"""
    raw = (raw or "").strip()
    if not raw:
        return None
    if '|' in raw:
        scope, lesson = raw.split('|', 1)
        return scope.strip(), lesson.strip()
    return "", raw


async def _maybe_propose_lessons(update: Update, uid: int, claude_output: str, user_text: str):
    """从 Claude 输出抽取 [LESSON: ...] 标记，逐条弹按钮（非工作内容 / 用户教学场景）"""
    matches = _LESSON_RE.findall(claude_output)
    for raw in matches:
        parsed = _parse_lesson_marker(raw)
        if not parsed:
            continue
        scope, lesson = parsed
        if not lesson:
            continue
        await _propose_lesson(update, uid, scope=scope, lesson=lesson, related_question=user_text)


def _auto_persist_work_lessons(uid: int, user_text: str, claude_output: str) -> list[int]:
    """工作内容完成后：静默入库 [LESSON] 标记，供下次 prompt 直接命中。"""
    saved: list[int] = []
    for raw in _LESSON_RE.findall(claude_output or ""):
        parsed = _parse_lesson_marker(raw)
        if not parsed:
            continue
        scope, lesson = parsed
        if not lesson:
            continue
        lid = db.add_lesson(
            owner_user_id=uid,
            source='work_auto',
            scope=scope,
            lesson=lesson,
            related_question=user_text[:500],
        )
        saved.append(lid)
        log.info("[work_memory] auto lesson #%s scope=%s", lid, scope or '(通用)')
    return saved


async def cb_lesson(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """inline 按钮回调：lesson:<action>:<token>"""
    q = update.callback_query
    await q.answer()
    try:
        _, action, token = q.data.split(':', 2)
    except ValueError:
        return
    pending = _pending_lessons.pop(token, None)
    if not pending:
        try:
            await q.edit_message_text("⚠️ 这条规则已过期或已处理")
        except (BadRequest, TimedOut):
            pass
        return
    uid = pending['uid']
    user_clicked = q.from_user.id
    if user_clicked != uid and not db.is_superuser(user_clicked):
        try:
            await q.edit_message_text("⚠️ 不是你的待确认规则，无权操作")
        except (BadRequest, TimedOut):
            pass
        return
    scope = pending['scope']
    lesson = pending['lesson']
    related = pending['related_question']
    if action == 'save':
        lid = db.add_lesson(
            owner_user_id=uid, source='auto', scope=scope, lesson=lesson,
            related_question=related,
        )
        await q.edit_message_text(f"✅ 已保存为你私有规则 #{lid}\n   范围：{scope}\n   规则：{lesson}")
    elif action == 'public':
        if not db.is_superuser(user_clicked):
            await q.edit_message_text("⚠️ 仅管理员可存为公共")
            return
        lid = db.add_lesson(
            owner_user_id=None, source='auto', scope=scope, lesson=lesson,
            related_question=related,
        )
        await q.edit_message_text(f"🌐 已保存为公共规则 #{lid}\n   范围：{scope}\n   规则：{lesson}")
    elif action == 'cancel':
        await q.edit_message_text("❌ 已取消，没存")


def _cleanup_pending_lessons():
    """5 分钟过期的清掉"""
    now = time.time()
    expired = [k for k, v in _pending_lessons.items() if v.get('expire_at', 0) < now]
    for k in expired:
        _pending_lessons.pop(k, None)


# ── Admin 选私有 / 公共（rule / alias / lesson 共用） ──

# token -> {kind, uid, payload, expire_at}
_pending_admin_save: dict[str, dict] = {}


async def _admin_choose_scope(update: Update, *, kind: str, payload: dict, description: str):
    """管理员加 rule/alias/lesson 时弹按钮二选一"""
    uid = update.effective_user.id
    token = _new_token()
    _pending_admin_save[token] = {
        'kind': kind,
        'uid': uid,
        'payload': payload,
        'expire_at': time.time() + 300,
    }
    keyboard = [[
        InlineKeyboardButton("👤 我私有", callback_data=f"adminsave:private:{token}"),
        InlineKeyboardButton("🌐 公共", callback_data=f"adminsave:public:{token}"),
    ], [
        InlineKeyboardButton("❌ 取消", callback_data=f"adminsave:cancel:{token}"),
    ]]
    await _send_user_message(
        update,
        f"你是管理员，想存为哪种？\n\n{description}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown',
    )


async def cb_admin_save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """adminsave:<scope>:<token>"""
    q = update.callback_query
    await q.answer()
    try:
        _, scope_choice, token = q.data.split(':', 2)
    except ValueError:
        return
    pending = _pending_admin_save.pop(token, None)
    if not pending:
        try:
            await q.edit_message_text("⚠️ 这个待存请求已过期或已处理")
        except (BadRequest, TimedOut):
            pass
        return
    if q.from_user.id != pending['uid']:
        try:
            await q.edit_message_text("⚠️ 不是你发起的，无权操作")
        except (BadRequest, TimedOut):
            pass
        return

    if scope_choice == 'cancel':
        try:
            await q.edit_message_text("❌ 已取消，没存")
        except (BadRequest, TimedOut):
            pass
        return

    owner = None if scope_choice == 'public' else pending['uid']
    kind = pending['kind']
    p = pending['payload']
    label_owner = "🌐 公共" if scope_choice == 'public' else "👤 私有"

    try:
        if kind == 'rule':
            rid = db.add_query_rule(p['table_pattern'], p['rule'], owner_user_id=owner)
            await q.edit_message_text(
                f"✅ 规则 #{rid} 已存（{label_owner}）\n"
                f"   表 `{p['table_pattern']}` — {p['rule']}",
                parse_mode='Markdown',
            )
        elif kind == 'alias':
            if owner is None:
                # 公共别名应该写 aliases.md，但我们 DB 没公共别名表；提示
                await q.edit_message_text(
                    "⚠️ 公共别名要写到 `omdb/.claude/database/aliases.md` 文件里。\n"
                    "DB 只存私有别名。这次没存。",
                    parse_mode='Markdown',
                )
            else:
                aid = db.add_user_alias(owner, p['alias'], p['target'])
                await q.edit_message_text(
                    f"✅ 别名 #{aid} 已存（{label_owner}）\n"
                    f"   {p['alias']} => `{p['target']}`",
                    parse_mode='Markdown',
                )
        elif kind == 'lesson':
            lid = db.add_lesson(
                owner_user_id=owner, source='manual',
                scope=p['scope'], lesson=p['lesson'],
                related_question=None,
            )
            await q.edit_message_text(
                f"✅ Lesson #{lid} 已存（{label_owner}）\n"
                f"   范围：{p['scope'] or '(无)'}\n"
                f"   规则：{p['lesson']}"
            )
        else:
            await q.edit_message_text(f"⚠️ 未知 kind={kind}")
    except Exception as e:
        log.error(f"[admin_save] {e}")
        try:
            await q.edit_message_text(f"❌ 存失败：{e}")
        except (BadRequest, TimedOut):
            pass


# ── Feedback 按钮（答完主动征询） ──

# token -> {uid, user_text, sql, result_brief, expire_at}
_pending_feedback: dict[str, dict] = {}


async def _ask_feedback_after_sql(job: 'query_queue.QueryJob', result_brief: str):
    """SQL 出结果后新发消息征询 👍/👎"""
    chat_id = job.meta.get('tg_chat_id') or job.chat_id
    user_text = job.meta.get('user_text') or ""
    token = _new_token()
    _pending_feedback[token] = {
        'uid': job.user_id,
        'user_text': user_text,
        'sql': job.sql,
        'result_brief': result_brief,
        'expire_at': time.time() + 1800,
    }
    keyboard = [[
        InlineKeyboardButton("👍 满意", callback_data=f"feedback:ok:{token}"),
        InlineKeyboardButton("👎 不对，告诉我哪不对", callback_data=f"feedback:bad:{token}"),
    ]]
    try:
        await _send_chat_message(
            chat_id,
            "这个回答合适吗？",
            mention_prefix=job.meta.get('mention_prefix'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        log.warning(f"[feedback] ask failed: {e}")


async def cb_feedback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """feedback:<action>:<token>"""
    q = update.callback_query
    await q.answer()
    try:
        _, action, token = q.data.split(':', 2)
    except ValueError:
        return
    pending = _pending_feedback.pop(token, None)
    if not pending:
        try:
            await q.edit_message_text("⚠️ 这个反馈窗口已过期")
        except (BadRequest, TimedOut):
            pass
        return
    uid = pending['uid']
    if q.from_user.id != uid and not db.is_superuser(q.from_user.id):
        try:
            await q.edit_message_text("⚠️ 不是你的反馈窗口")
        except (BadRequest, TimedOut):
            pass
        return

    if action == 'ok':
        try:
            await q.edit_message_text("👍 谢谢反馈")
        except (BadRequest, TimedOut):
            pass
        return

    if action == 'bad':
        # 反思流程：把 Q+SQL+结果喂给 Claude，让它自己 emit [LESSON]
        try:
            await q.edit_message_text("🤔 在想哪里错了，让我抽一条规则给你确认...")
        except (BadRequest, TimedOut):
            pass
        await _reflect_and_propose(
            chat_id=q.message.chat_id,
            uid=uid,
            user_text=pending['user_text'],
            sql=pending['sql'],
            result_brief=pending['result_brief'],
            origin_msg_id=q.message.message_id,
        )


async def _reflect_and_propose(*, chat_id: int, uid: int, user_text: str,
                                sql: str, result_brief: str, origin_msg_id: int | None):
    """喂 Claude 一段反思 prompt，期待它 emit [LESSON: ...]，再走现有 propose 流程"""
    reflection_prompt = (
        "用户对刚才的查询答案表示**不满意**，需要你反思。\n\n"
        "原始问题：\n" + (user_text or '(空)') + "\n\n"
        "执行的 SQL：\n" + (sql or '(空)') + "\n\n"
        "结果摘要：\n" + (result_brief[:600] if result_brief else '(空)') + "\n\n"
        "请只做一件事：用 1 句话指出哪里偏了（比如『按 app 拆了用户没要』、『列名错了』、"
        "『过滤条件多了』等），并 emit **1 条** [LESSON: <scope> | <rule>] 标记，"
        "不要写其他内容。"
    )
    loop = asyncio.get_event_loop()

    def run_claude():
        return ai_client.chat_stream(
            system_prompt="",  # 反思简短，不挂大 prompt
            messages=[{"role": "user", "content": reflection_prompt}],
            on_chunk=lambda c: None,
            is_superuser=db.is_superuser(uid),
            task_type='learn',
        )

    try:
        chat_result = await loop.run_in_executor(None, run_claude)
    except Exception as e:
        log.warning(f"[feedback] reflection claude failed: {e}")
        return

    out = chat_result.text if hasattr(chat_result, 'text') else str(chat_result or '')
    # 抽 [LESSON: ...]
    matches = _LESSON_RE.findall(out or "")
    if not matches:
        try:
            await _bot_app.bot.send_message(
                chat_id=chat_id,
                text=(
                    "我没能从反思里抽出明确规则。直接告诉我"
                    "「哪里不对 / 以后该怎么做」，我会自动学。\n\n"
                    f"Claude 反思原文：\n{(out or '(空)')[:500]}"
                ),
            )
        except Exception:
            pass
        return

    # 挑第一条提案
    parsed = _parse_lesson_marker(matches[0])
    if not parsed:
        return
    scope, lesson = parsed
    if not lesson:
        return

    # 弹按钮（构造一个最小 update.message-like 对象不方便，直接用 _bot_app.bot 发）
    token = _new_token()
    _pending_lessons[token] = {
        'uid': uid,
        'scope': scope,
        'lesson': lesson,
        'related_question': user_text,
        'expire_at': time.time() + 300,
    }
    text = (
        f"📚 我反思了一下，建议记住：\n\n"
        f"   • 范围：{scope or '(无)'}\n"
        f"   • 规则：{lesson}\n\n"
        f"以后碰到类似问题会自动应用。要存吗？"
    )
    is_admin = db.is_superuser(uid)
    keyboard = [[
        InlineKeyboardButton("✅ 存为我私有", callback_data=f"lesson:save:{token}"),
    ]]
    if is_admin:
        keyboard[0].append(
            InlineKeyboardButton("🌐 存为公共", callback_data=f"lesson:public:{token}")
        )
    keyboard.append([InlineKeyboardButton("❌ 取消", callback_data=f"lesson:cancel:{token}")])
    try:
        kwargs = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': InlineKeyboardMarkup(keyboard),
        }
        await _bot_app.bot.send_message(**kwargs)
    except Exception as e:
        log.warning(f"[feedback] propose lesson failed: {e}")


# ── SQL queue ──

# [SQL: ...]：默认 CSV 策略 = auto（按结果大小自动决定发不发）
# [SQL_FILE: ...]：强制发 CSV（用户明确要文件 / 完整数据）
# 用 capture group 区分两者
_SQL_RE = re.compile(r'\[(SQL|SQL_FILE):\s*(.+?)\]', re.DOTALL)


async def _enqueue_sql_blocks(update: Update, text: str, uid: int, *, task_id: str, user_text: str = ""):
    matches = _SQL_RE.findall(text)  # list of (marker, sql)
    if not matches:
        return
    queue = query_queue.get_queue()
    for marker, sql in matches:
        sql = sql.strip()
        if not sql:
            continue
        csv_policy = 'always' if marker == 'SQL_FILE' else 'auto'
        job, ahead = queue.submit(
            sql=sql,
            user_id=uid,
            chat_id=update.effective_chat.id,
            label=f"task_{task_id[-6:]}",
        )
        head = "🔍 SQL 已开始执行" if ahead == 0 else f"📥 SQL 已加入队列，前面还有 {ahead} 个任务"
        body = f"{head}\n\n{_truncate(sql, 1500)}"
        await _reply_user(update, body)
        job.meta['tg_chat_id'] = update.effective_chat.id
        job.meta['user_text'] = user_text
        job.meta['mention_prefix'] = _mention_prefix(update)
        job.meta['csv_policy'] = csv_policy  # 'always' 或 'auto'


def _truncate(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n - 3] + "..."


def _q_snippet(s: str, n: int = 80) -> str:
    s = (s or "").strip().replace('\n', ' ')
    return s if len(s) <= n else s[:n - 3] + "..."


def _with_quote(user_text: str, body: str) -> str:
    """已弃用：保留签名兼容，直接返回 body。"""
    return body


async def _claude_summarize(*, user_text: str, sql: str, status: str,
                             rows: int, preview: str, error: str | None,
                             has_csv: bool, csv_filename: str | None,
                             is_superuser: bool) -> str:
    """让 Claude 看着 SQL 结果给一段自然语言中文回答。返回纯文本。"""
    if status == 'fail':
        body = (
            f"用户问：\n{user_text}\n\n"
            f"我跑了这条 SQL：\n{sql}\n\n"
            f"但失败了，mysql 报错：\n{error}\n\n"
            "请基于错误用 1-3 句话告诉用户**问题在哪 + 怎么改**（如列名不存在就指出实际列名、"
            "类型不匹配就提示转换等），不要复述完整 SQL。不要 emit 任何 [SQL] / [LESSON] / "
            "[SEND_FILE] 标记。"
        )
    elif status == 'empty':
        body = (
            f"用户问：\n{user_text}\n\n"
            f"我跑了这条 SQL：\n{sql}\n\n"
            "结果是 **0 行**（查询执行成功但没数据）。\n\n"
            "请基于这个事实用 1-2 句话直接回答用户。如果用户问的是 yes/no（如『有没有 X』），"
            "直接回答『没有』；如果是统计问，告诉用户当前条件下没数据。不要 emit 任何标记。"
        )
    else:  # ok
        csv_hint = (
            f"完整数据已生成 CSV 附件 `{csv_filename}` 同时发给用户。" if has_csv
            else "结果不大，没有附 CSV（如果要文件用户会要求）。"
        )
        body = (
            f"用户问：\n{user_text}\n\n"
            f"我跑了这条 SQL：\n{sql}\n\n"
            f"返回 **{rows} 行**；预览：\n\n{preview}\n\n"
            f"{csv_hint}\n\n"
            "请用**自然中文**直接回答用户的问题，按情况灵活：\n"
            "- 单一数字 → 给数字 + 必要单位（金额已经 ÷100 换元的就直接说元；没换的提醒）\n"
            "- 多行结果 → 给一句洞察（top 3 是什么 / 占比 / 变化），需要列举可附简短 markdown 表\n"
            "- 大量数据 → 一句总结 + 提示看 CSV 附件\n"
            "- yes/no 问题 → 直接『有/没有』+ 关键证据\n\n"
            "不要复述完整 SQL（用户不在乎）；不要 emit 任何 [SQL] / [LESSON] / [SEND_FILE] 标记。"
            "回答控制在 200 字以内，除非有必要列表格。"
        )
    loop = asyncio.get_event_loop()
    def run():
        try:
            return ai_client.chat_stream(
                system_prompt="",
                messages=[{"role": "user", "content": body}],
                on_chunk=lambda c: None,
                is_superuser=is_superuser,
                task_type='fast',
            )
        except Exception as e:
            log.warning(f"[summarize] claude failed: {e}")
            return ""
    summary_result = await loop.run_in_executor(None, run)
    summary = (summary_result.text if hasattr(summary_result, 'text') else str(summary_result or "")).strip()
    # 保险：去掉任何 [SQL] / [LESSON] / [SEND_FILE] 残留
    summary = re.sub(r'\[(SQL|SQL_FILE|LESSON|SEND_FILE|REMIND):\s*.*?\]', '', summary, flags=re.DOTALL).strip()
    return summary


async def _on_query_done(job: 'query_queue.QueryJob'):
    """worker 跑完一条 SQL 后：新发消息 @提问者（自然语言总结 + 必要时附 CSV）"""
    res = job.result
    chat_id = job.chat_id
    elapsed = f"{(job.finished_at or 0) - (job.started_at or 0):.1f}s"
    user_text = job.meta.get('user_text') or ""
    is_su = db.is_superuser(job.user_id)

    if res is None:
        await _send_job_message(job, f"❌ SQL 完成但 result 为 None（{elapsed}）")
        await _ask_feedback_after_sql(job, "result=None")
        return

    # 1. 决定要不要发 CSV
    if res.ok and res.rows > 0:
        policy = job.meta.get('csv_policy', 'auto')
        if policy == 'never':
            send_csv = False
        elif policy == 'always':
            send_csv = True
        else:
            send_csv = res.rows > CSV_INLINE_THRESHOLD_ROWS or res.truncated
    else:
        send_csv = False

    # 2. 让 Claude 看着结果给自然语言答案
    if not res.ok:
        status = 'fail'
    elif res.rows == 0:
        status = 'empty'
    else:
        status = 'ok'

    csv_filename = os.path.basename(res.csv_path) if (send_csv and res.csv_path) else None
    summary = await _claude_summarize(
        user_text=user_text,
        sql=job.sql,
        status=status,
        rows=res.rows,
        preview=res.preview or "",
        error=res.error,
        has_csv=send_csv,
        csv_filename=csv_filename,
        is_superuser=is_su,
    )

    # 4. 终态：状态行 + Claude 总结
    if status == 'fail':
        head = f"❌ SQL 失败（{elapsed}）"
    elif status == 'empty':
        head = f"✅ 查询完成（0 行 / {elapsed}）"
    else:
        head = f"✅ 查询完成（{res.rows} 行 / {elapsed}）"
        if res.truncated:
            head += " · 已截断，详见 CSV"
        elif send_csv:
            head += " · CSV 已附"

    if summary:
        body = f"{head}\n\n{summary}"
    else:
        # Claude 总结挂了，退回到旧式 head + preview
        if status == 'ok' and res.preview:
            body = f"{head}\n\n{res.preview}"
        elif status == 'fail':
            body = f"{head}\n\n{res.error or '未知错误'}"
        else:
            body = head
    if len(body) > 3800:
        body = body[:3800] + "..."
    await _send_job_message(job, body)

    # 4. CSV 单独发
    if send_csv and res.csv_path and os.path.isfile(res.csv_path):
        try:
            with open(res.csv_path, 'rb') as fh:
                kwargs = {
                    'chat_id': chat_id,
                    'document': fh,
                    'filename': os.path.basename(res.csv_path),
                    'caption': f"📄 {res.rows} 行 — {os.path.basename(res.csv_path)}",
                }
                await _bot_app.bot.send_document(**kwargs)
        except Exception as e:
            log.warning(f"[SQL] send csv failed: {e}")

    # 6. 答完了征询 👍 / 👎
    result_brief = summary[:500] if summary else (res.preview or f"{res.rows} 行")[:500]
    await _ask_feedback_after_sql(job, result_brief)


# ── Reminders ──

async def _parse_reminders(update: Update, text: str):
    for match in re.finditer(r'\[REMIND:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+(.+?)\]', text):
        remind_at, message = match.group(1), match.group(2).strip()
        uid = update.effective_user.id
        chat_id = update.effective_chat.id
        db.create_reminder(uid, chat_id, remind_at, message)
        await _send_user_message(update,f"⏰ 提醒已设置：{remind_at}\n📝 {message}")

async def _reminder_checker(app):
    while True:
        await asyncio.sleep(30)
        try:
            for r in db.get_due_reminders():
                try:
                    await app.bot.send_message(chat_id=r['chat_id'], text=f"⏰ *提醒*\n\n{r['message']}", parse_mode='Markdown')
                    db.mark_reminder_sent(r['id'])
                except Exception as e:
                    log.error(f"[REMIND] send failed: {e}")
        except Exception as e:
            log.error(f"[REMIND] checker error: {e}")

# ── Main ──

async def cmd_askant(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not check_auth(uid):
        return
    question = ' '.join(ctx.args).strip()
    if not question:
        await _reply_user(
            update,
            "用法: /askant 你的问题\n"
            "（经 agent-bus 转问工作狂人；直接问又初请正常发消息即可）",
        )
        return
    from worker_ant_bus import ask_worker_ant_via_bus, bus_ask_ready

    if not bus_ask_ready():
        await _reply_user(update, "agent-bus 未配置（需 dc-platform.json 的 base_url + token）")
        return
    await _reply_user(update, task_ack(kind='ask_ant', in_group=_is_group_chat(update)))
    try:
        reply = await ask_worker_ant_via_bus(question)
        for part in split_message(f"🐜 工作狂人（agent-bus）：\n{reply}"):
            await _send_user_message(update, part)
    except Exception as exc:
        log.error("[askant] %s", exc)
        await _send_user_message(update, f"❌ 问工作狂人失败: {exc}")


async def cmd_queue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update.effective_user.id):
        return
    n = query_queue.get_queue().queue_size()
    if n == 0:
        await _send_user_message(update,"📥 SQL 队列为空")
    else:
        await _send_user_message(update,f"📥 SQL 队列：{n} 个任务（含正在跑的 1 个）")


# 全局引用：查询完成回调要靠它向用户发消息
_bot_app = None


def main():
    global _bot_app
    if not TG_BOT_TOKEN:
        print("Error: TG_BOT_TOKEN not set in .env")
        return

    # Init DB with default auth
    try:
        group_reply_style.ensure_style_lesson()
    except Exception:
        pass
    for uid in ALLOWED_USERS:
        db.authorize(uid, 'admin')
    for uid in GROUP_ALLOWED_USERS:
        if uid not in ALLOWED_USERS:
            db.authorize(uid, 'operator')

    # concurrent_updates=True 让多个用户的消息可以同时进 handle_message
    # （否则默认串行，一条没处理完后面所有人都会卡住）
    app = (
        Application.builder()
        .token(TG_BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )
    _bot_app = app

    app.add_handler(CommandHandler(["start", "help"], cmd_help))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("tasks", cmd_tasks))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("addrule", cmd_addrule))
    app.add_handler(CommandHandler("delrule", cmd_delrule))
    app.add_handler(CommandHandler("aliases", cmd_aliases))
    app.add_handler(CommandHandler("addalias", cmd_addalias))
    app.add_handler(CommandHandler("delalias", cmd_delalias))
    app.add_handler(CommandHandler("teach", cmd_teach))
    app.add_handler(CommandHandler("lessons", cmd_lessons))
    app.add_handler(CommandHandler("grant", cmd_grant))
    app.add_handler(CommandHandler("revoke", cmd_revoke))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CallbackQueryHandler(cb_lesson, pattern=r"^lesson:"))
    app.add_handler(CallbackQueryHandler(cb_feedback, pattern=r"^feedback:"))
    app.add_handler(CallbackQueryHandler(cb_admin_save, pattern=r"^adminsave:"))
    app.add_handler(CommandHandler("reminders", cmd_reminders))
    app.add_handler(CommandHandler("sendfile", cmd_sendfile))
    app.add_handler(CommandHandler("queue", cmd_queue))
    app.add_handler(CommandHandler("askant", cmd_askant))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def post_init(application):
        asyncio.create_task(_reminder_checker(application))
        loop = asyncio.get_event_loop()
        query_queue.get_queue().attach(loop, _on_query_done)
        log.info("[query_queue] worker attached")
        n = db.cancel_stuck_tasks()
        if n:
            log.info(f"[startup] cancelled {n} stuck in_progress task(s)")
        if WORKER_ANT_LEARN_ENABLED:
            asyncio.create_task(backfill_unprocessed())
        if WORKER_ANT_UPGRADE_ENABLED:
            import worker_ant_directives as wad
            auth = wad.ensure_authorized(note='主人授权：工作指令+流程升级指令落地改本地实现')
            log.info('[startup] worker_ant authorized scope=%s', auth.get('scope'))
        await start_dispatch_watcher(application)
        await start_agent_bus_watcher(application)
        await start_workbook_watcher(application)
        await start_jike_checkin_scheduler()
        try:
            from agent_bus_catchup import run_catchup
            asyncio.create_task(run_catchup(application, reason='tgbot_startup'))
        except Exception as exc:
            log.warning('[startup] agent-bus catchup skip: %s', exc)
        asyncio.create_task(self_check_loop(application))
        asyncio.create_task(heartbeat_loop(application))

    app.post_init = post_init

    log.info(f"🤖 数据中心 TG Bot starting... mode={ai_client.mode_name()}")
    log.info(f"📂 Project: {PROJECT_ROOT}")
    if ALLOWED_GROUP_CHAT_IDS:
        log.info(
            "Allowed group chats: %s (listen_without_mention=%s, observe_all=%s)",
            ALLOWED_GROUP_CHAT_IDS, GROUP_LISTEN_WITHOUT_MENTION, GROUP_OBSERVE_ALL,
        )
    app.run_polling(drop_pending_updates=os.getenv('TGBOT_DROP_PENDING_UPDATES', 'false').strip().lower() in (
        '1', 'true', 'yes', 'on',
    ))

if __name__ == '__main__':
    main()
