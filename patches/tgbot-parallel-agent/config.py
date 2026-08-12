import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ALLOWED_USERS = [int(x) for x in os.getenv('ALLOWED_USERS', '').split(',') if x.strip().isdigit()]
GROUP_ALLOWED_USERS = [
    int(x) for x in os.getenv('GROUP_ALLOWED_USERS', '').split(',') if x.strip().isdigit()
]
ALLOWED_GROUP_CHAT_IDS = [
    int(x) for x in os.getenv('ALLOWED_GROUP_CHAT_IDS', '').split(',') if x.strip().lstrip('-').isdigit()
]
GROUP_LISTEN_WITHOUT_MENTION = os.getenv('GROUP_LISTEN_WITHOUT_MENTION', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# 群聊旁听：白名单群内所有消息写入统一上下文；仅 @本机器人 才在群里回复（正文提「初儿」不算）
GROUP_OBSERVE_ALL = os.getenv('GROUP_OBSERVE_ALL', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# 旁听消息不写 tg_status、不推又初私聊（默认关）；派给又初的群消息/agent-bus 仍镜像
TG_MIRROR_GROUP_OBSERVE = os.getenv('TG_MIRROR_GROUP_OBSERVE', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'tgbot.db')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-6')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '8192'))

# AI backend: cursor (default) | claude
AI_BACKEND = os.getenv('AI_BACKEND', 'cursor').strip().lower()
CURSOR_API_KEY = os.getenv('CURSOR_API_KEY', '')
CURSOR_MODEL = os.getenv('CURSOR_MODEL', 'composer-2.5')
# 按任务类型选模型（token 充足时可分开配置快慢模型）
CURSOR_MODEL_FAST = os.getenv('CURSOR_MODEL_FAST', 'composer-2.5-fast')
CURSOR_MODEL_WORK = os.getenv('CURSOR_MODEL_WORK', CURSOR_MODEL)
CURSOR_MODEL_LEARN = os.getenv('CURSOR_MODEL_LEARN', CURSOR_MODEL_FAST)
CURSOR_MODEL_SUMMARIZE = os.getenv('CURSOR_MODEL_SUMMARIZE', CURSOR_MODEL_FAST)
# 全局 fallback 链（逗号分隔）；某模型 token 用尽时自动换下一个
_fallback_raw = os.getenv('CURSOR_MODEL_FALLBACK_CHAIN', '').strip()
CURSOR_MODEL_FALLBACK_CHAIN = [
    x.strip() for x in _fallback_raw.split(',') if x.strip()
] or ['composer-2.5-fast', 'composer-2.5', 'gpt-5.3-codex', 'claude-4.6-sonnet-medium-thinking']
# 本地标记「额度用尽」后多少小时再尝试该模型
MODEL_QUOTA_RESET_HOURS = int(os.getenv('MODEL_QUOTA_RESET_HOURS', '6'))
AI_TIMEOUT_SEC = int(os.getenv('AI_TIMEOUT_SEC', '600'))  # 已废弃作软超时；保留兼容
# 子进程存活探活间隔（秒）；仅用于内部检测，默认不向 TG 刷「还在处理」
AI_PROGRESS_INTERVAL_SEC = int(os.getenv('AI_PROGRESS_INTERVAL_SEC', '60'))
# 硬上限（秒）；0=不按墙钟杀。优先用 AI_IDLE_TIMEOUT_SEC（无 stdout 则杀）
AI_HARD_TIMEOUT_SEC = int(os.getenv('AI_HARD_TIMEOUT_SEC', '0'))
# 无 stdout 响应超时（秒）；默认 900=15 分钟无输出则 kill，释放 agent 队列
AI_IDLE_TIMEOUT_SEC = int(os.getenv('AI_IDLE_TIMEOUT_SEC', '900'))
# 私聊叠单：长活占着 agent 时，新私聊另开并行 agent（不 resume 旧 chat）
AGENT_PARALLEL_WHEN_BUSY = os.getenv('AGENT_PARALLEL_WHEN_BUSY', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# 并行软顶（含正在跑的串行任务占用的名额之外的并行槽上限）
AGENT_MAX_PARALLEL = int(os.getenv('AGENT_MAX_PARALLEL', '3'))
# 新开并行 agent 前是否刷新 bootstrap（跑 load-memory-context.sh）
AGENT_MEMORY_REFRESH_ON_SPAWN = os.getenv('AGENT_MEMORY_REFRESH_ON_SPAWN', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# 私聊「还在处理中」刷屏间隔；0=关闭（推荐）。长任务不要一直占 TG 私聊
SLOW_NUDGE_SEC = int(os.getenv('SLOW_NUDGE_SEC', '0'))
# 是否在 TG 私聊推送 cursor-agent 心跳「还在处理」（默认关）
TG_AGENT_HEARTBEAT_NOTIFY = os.getenv('TG_AGENT_HEARTBEAT_NOTIFY', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# agent-bus 未结案「进度」镜像推私聊（默认关，避免长任务刷屏）
AGENT_BUS_PROGRESS_ENABLED = os.getenv('AGENT_BUS_PROGRESS_ENABLED', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)

# Project root：默认 dc-parent（问数/ETL）；可通过环境变量覆盖
TGBOT_DIR = os.path.dirname(os.path.abspath(__file__))
OMDB_DIR = os.path.abspath(os.path.join(TGBOT_DIR, '..'))
_DEFAULT_ROOT = os.path.abspath(os.path.join(OMDB_DIR, '..'))
PROJECT_ROOT = os.getenv('TGBOT_PROJECT_ROOT', _DEFAULT_ROOT)

# DB / 元数据 / 别名
MY_CNF_PATH = os.path.join(OMDB_DIR, '.claude', 'database', 'my.cnf')
ALIASES_PATH = os.path.join(OMDB_DIR, '.claude', 'database', 'aliases.md')
METADATA_DB_PATH = os.path.join(OMDB_DIR, 'data', 'metadata.db')

# TG 文件交换目录（必须能在不同用户身份下读写）
INCOMING_DIR = os.path.join(TGBOT_DIR, 'incoming')
OUTGOING_DIR = os.path.join(TGBOT_DIR, 'outgoing')
os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(OUTGOING_DIR, exist_ok=True)
try:
    os.chmod(INCOMING_DIR, 0o777)
    os.chmod(OUTGOING_DIR, 0o777)
except OSError:
    pass

# 数据查询限制
QUERY_TIMEOUT_SEC = int(os.getenv('QUERY_TIMEOUT_SEC', '120'))
QUERY_MAX_ROWS = int(os.getenv('QUERY_MAX_ROWS', '50000'))

# 自动发 CSV 的阈值：行数超过这个 + policy=auto 才发；不超过就只回预览
# 与 _render_preview 的 max_preview_rows=10 对齐：超出预览能显示的就发 CSV，
# 否则用户在聊天里看不全。
CSV_INLINE_THRESHOLD_ROWS = int(os.getenv('CSV_INLINE_THRESHOLD_ROWS', '10'))

# ── 工作狂人 / Agent 互通（Telethon 旁听 + HTTP 桥提问）──
WORKER_ANT_BOT = os.getenv('WORKER_ANT_BOT', 'worker_ant_bot').strip().lstrip('@')
_raw_monitor = os.getenv('MONITOR_GROUP_CHAT_ID', '').strip()
if not _raw_monitor:
    _raw_monitor = (os.getenv('ALLOWED_GROUP_CHAT_IDS', '-5376962870') or '-5376962870').split(',')[0].strip()
MONITOR_GROUP_CHAT_ID = int(_raw_monitor) if _raw_monitor.lstrip('-').isdigit() else -5376962870

# 监控群聊上下文：定时归档到 ~/.dc-platform/memory/group_chat/，瘦身 context.jsonl
GROUP_CONTEXT_ARCHIVE_ENABLED = os.getenv('GROUP_CONTEXT_ARCHIVE_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
GROUP_CONTEXT_KEEP_LINES = int(os.getenv('GROUP_CONTEXT_KEEP_LINES', '150'))
GROUP_CONTEXT_HOT_HOURS = int(os.getenv('GROUP_CONTEXT_HOT_HOURS', '24'))
GROUP_CONTEXT_ARCHIVE_INTERVAL_SEC = int(os.getenv('GROUP_CONTEXT_ARCHIVE_INTERVAL_SEC', '21600'))

# 居家办公随机抽查群：被 @ 时自动算题回复（Telethon 真人号）
ATTENDANCE_CHECK_ENABLED = os.getenv('ATTENDANCE_CHECK_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
_raw_attendance_chat = os.getenv('ATTENDANCE_CHECK_CHAT_ID', '-1003332772579').strip()
ATTENDANCE_CHECK_CHAT_ID = (
    int(_raw_attendance_chat) if _raw_attendance_chat.lstrip('-').isdigit() else -1003332772579
)
ATTENDANCE_CHECK_USERNAME = os.getenv('ATTENDANCE_CHECK_USERNAME', 'youchu8888').strip().lstrip('@')
_attendance_uid_raw = os.getenv('ATTENDANCE_CHECK_USER_ID', '').strip()
if _attendance_uid_raw.isdigit():
    ATTENDANCE_CHECK_USER_ID = int(_attendance_uid_raw)
else:
    ATTENDANCE_CHECK_USER_ID = ALLOWED_USERS[0] if ALLOWED_USERS else 0
ATTENDANCE_CHECK_DELAY_MIN_SEC = int(os.getenv('ATTENDANCE_CHECK_DELAY_MIN_SEC', '10'))
ATTENDANCE_CHECK_DELAY_MAX_SEC = int(os.getenv('ATTENDANCE_CHECK_DELAY_MAX_SEC', '25'))

# 极客小助手 @jike1024_bot 定时签到/签出（Telethon 真人号私聊）
JIKE_CHECKIN_ENABLED = os.getenv('JIKE_CHECKIN_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
JIKE_BOT_USERNAME = os.getenv('JIKE_BOT_USERNAME', 'jike1024_bot').strip().lstrip('@')
# 打卡时间窗（HH:MM，Asia/Shanghai）：在窗口内随机选一刻执行
JIKE_CHECKIN_WINDOW_START = os.getenv('JIKE_CHECKIN_WINDOW_START', '09:30').strip()
JIKE_CHECKIN_WINDOW_END = os.getenv('JIKE_CHECKIN_WINDOW_END', '10:00').strip()
JIKE_CHECKOUT_WINDOW_START = os.getenv('JIKE_CHECKOUT_WINDOW_START', '22:00').strip()
JIKE_CHECKOUT_WINDOW_END = os.getenv('JIKE_CHECKOUT_WINDOW_END', '22:30').strip()
JIKE_CHECKIN_STATE_PATH = os.path.join(TGBOT_DIR, 'data', 'jike_checkin_state.json')

GROUP_ROLL_CALL_ENABLED = os.getenv('GROUP_ROLL_CALL_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
GROUP_ROLL_CALL_SENDERS = [
    x.strip()
    for x in os.getenv(
        'GROUP_ROLL_CALL_SENDERS',
        '知秋,工作狂人,worker_ant,zhiqiu,worker_ant_bot',
    ).split(',')
    if x.strip()
]

GROUP_WORKBOOK_PROGRESS_ENABLED = os.getenv(
    'GROUP_WORKBOOK_PROGRESS_ENABLED', 'true',
).strip().lower() in ('1', 'true', 'yes', 'on')

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', '0') or '0')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '').strip()
USER_SESSION_PATH = os.getenv('USER_SESSION_PATH', os.path.join(TGBOT_DIR, 'data', 'user_telegram'))
TG_PROXY_URL = os.getenv('TG_PROXY_URL', '').strip() or None
# Telethon 设备信息（显示在 TG「设置→设备」；仅对新登录会话生效，需重登）
TELETHON_DEVICE_MODEL = os.getenv('TELETHON_DEVICE_MODEL', 'MacBook Pro').strip()
TELETHON_SYSTEM_VERSION = os.getenv('TELETHON_SYSTEM_VERSION', 'macOS 15.7.2').strip()
TELETHON_APP_VERSION = os.getenv('TELETHON_APP_VERSION', '6.4.2').strip()
# 仅工作时段跑 Telethon 旁听（旧机 bot.py 会 import；默认关=全天）
TELETHON_WORK_HOURS_ONLY = os.getenv('TELETHON_WORK_HOURS_ONLY', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
# 旧机 worker_ant_dispatch_watcher 工作在线时段（Asia/Shanghai）
TG_WORK_ONLINE_START = os.getenv('TG_WORK_ONLINE_START', '09:00').strip()
TG_WORK_ONLINE_END = os.getenv('TG_WORK_ONLINE_END', '22:00').strip()
TG_WORK_ONLINE_TZ = os.getenv('TG_WORK_ONLINE_TZ', 'Asia/Shanghai').strip()

# 进程内定期自查（Mac 常开保活；默认 2min，critical 1 次即重启）
BOT_SELF_CHECK_ENABLED = os.getenv('BOT_SELF_CHECK_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
BOT_SELF_CHECK_INTERVAL = int(os.getenv('BOT_SELF_CHECK_INTERVAL', '120'))
BOT_SELF_CHECK_NOTIFY_COOLDOWN = int(os.getenv('BOT_SELF_CHECK_NOTIFY_COOLDOWN', '900'))
BOT_HEARTBEAT_INTERVAL = int(os.getenv('BOT_HEARTBEAT_INTERVAL', '30'))
BOT_CRITICAL_RESTART_AFTER = int(os.getenv('BOT_CRITICAL_RESTART_AFTER', '3'))
BOT_SOFT_RESTART_AFTER = int(os.getenv('BOT_SOFT_RESTART_AFTER', '5'))
# 有 launchd/daemon 托管时，进程内 watchdog 默认只告警不抢着重启
BOT_SELF_CHECK_ALLOW_RESTART = os.getenv('BOT_SELF_CHECK_ALLOW_RESTART', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
DAEMON_PID_FILE = os.getenv('TGBOT_DAEMON_PID_FILE', '/tmp/tgbot-dc-daemon.pid')

# 旧 HTTP 桥（已废弃，问狂人请用 agent-bus；worker_ant_client 仍可读，默认留空）
WORKER_ANT_BRIDGE_URL = os.getenv('WORKER_ANT_BRIDGE_URL', '').strip().rstrip('/')
WORKER_ANT_BRIDGE_TOKEN = os.getenv('WORKER_ANT_BRIDGE_TOKEN', '').strip()
WORKER_ANT_BRIDGE_TIMEOUT = int(os.getenv('WORKER_ANT_BRIDGE_TIMEOUT', '180'))

# 经 agent-bus 问工作狂人：轮询等待回复
AGENT_BUS_ASK_TIMEOUT = int(os.getenv('AGENT_BUS_ASK_TIMEOUT', '120'))
AGENT_BUS_ASK_POLL_INTERVAL = int(os.getenv('AGENT_BUS_ASK_POLL_INTERVAL', '5'))
# 问狂人等待中：超过 N 秒仍无实质回复则催促 1 次（默认 300=5 分钟）；0=不催
AGENT_BUS_NUDGE_AFTER_SEC = int(os.getenv('AGENT_BUS_NUDGE_AFTER_SEC', '300'))

WORKER_ANT_INBOX_PATH = os.path.join(INCOMING_DIR, 'worker_ant_group_inbox.jsonl')

# 工作狂人群消息 → 自动整理上下文并沉淀 lesson / 工作记忆
WORKER_ANT_LEARN_ENABLED = os.getenv('WORKER_ANT_LEARN_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
WORKER_ANT_LEARN_CONTEXT_LINES = int(os.getenv('WORKER_ANT_LEARN_CONTEXT_LINES', '6'))

# TG agent-bus 展示模式：
#   status_mirror — 狂人原文 + 又初 ACK/回执/工作状态；lesson/心跳/重唤醒静默（默认）
#   incoming_only — 仅狂人原文，不镜像工作状态
#   full          — 旧行为：TG 内自动 ack、跑 Agent、推 lesson 摘要
AGENT_BUS_TG_MODE = os.getenv('AGENT_BUS_TG_MODE', 'status_mirror').strip().lower()
AGENT_BUS_STATUS_MIRROR = AGENT_BUS_TG_MODE == 'status_mirror'
AGENT_BUS_INCOMING_ONLY = AGENT_BUS_TG_MODE in (
    'incoming_only', 'inbox_only', 'minimal', 'status_mirror',
)

def _env_bool(key: str, default: str) -> bool:
    return os.getenv(key, default).strip().lower() in ('1', 'true', 'yes', 'on')

# 收到 agent-bus 派单时自动回复 / 执行（点名秒回，验数派单跑 Agent 后回传）
# incoming_only 下强制关闭，避免与 Cursor 主会话双跑
if AGENT_BUS_INCOMING_ONLY:
    WORKER_ANT_AUTO_REPLY = False
    WORKER_ANT_AUTO_EXECUTE = False
else:
    WORKER_ANT_AUTO_REPLY = _env_bool('WORKER_ANT_AUTO_REPLY', 'true')
    WORKER_ANT_AUTO_EXECUTE = _env_bool('WORKER_ANT_AUTO_EXECUTE', 'true')
# 工作狂人流程升级：按「具体怎么做」改 omdb/tgbot/ 本地实现（默认开，需 ensure_authorized）
WORKER_ANT_UPGRADE_ENABLED = os.getenv('WORKER_ANT_UPGRADE_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)

# 性能：规则判断（默认关 AI triage）、派单短 prompt、沉淀放后台
WORKER_ANT_AI_TRIAGE = os.getenv('WORKER_ANT_AI_TRIAGE', 'false').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
WORKER_ANT_LEARN_ASYNC = os.getenv('WORKER_ANT_LEARN_ASYNC', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
DISPATCH_LITE_PROMPT = os.getenv('DISPATCH_LITE_PROMPT', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)

# agent-bus 互通（youchu_ai ↔ worker_ant）→ TG 私聊通知
DC_PLATFORM_JSON = os.path.join(PROJECT_ROOT, '.claude', 'database', 'dc-platform.json')
AGENT_BUS_STATE_DIR = os.getenv(
    'AGENT_BUS_STATE_DIR',
    os.path.join(os.path.expanduser('~'), 'Library/Application Support/youchu-agent-bus/state'),
)
os.makedirs(AGENT_BUS_STATE_DIR, exist_ok=True)
AGENT_BUS_ENABLED = os.getenv('AGENT_BUS_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
AGENT_BUS_AGENT_NAME = os.getenv('AGENT_BUS_AGENT_NAME', 'youchu_ai').strip() or 'youchu_ai'
AGENT_BUS_POLL_INTERVAL = int(os.getenv('AGENT_BUS_POLL_INTERVAL', '15'))
AGENT_BUS_INBOX_PATH = os.path.join(INCOMING_DIR, 'worker_ant_agent_bus_inbox.jsonl')

# 工作狂人派单 → 本 Bot 私聊通知又初（需 Telethon + bot token）
WORKER_ANT_DISPATCH_ENABLED = os.getenv('WORKER_ANT_DISPATCH_ENABLED', 'true').strip().lower() in (
    '1', 'true', 'yes', 'on',
)
_dispatch_notify_raw = os.getenv('TASK_DISPATCH_NOTIFY_USER_IDS', '').strip()
TASK_DISPATCH_NOTIFY_USER_IDS = [
    int(x) for x in _dispatch_notify_raw.split(',') if x.strip().isdigit()
] or list(ALLOWED_USERS)

_roll_uid_raw = os.getenv('GROUP_ROLL_CALL_USER_IDS', '').strip()
if _roll_uid_raw:
    GROUP_ROLL_CALL_USER_IDS = [
        int(x) for x in _roll_uid_raw.split(',') if x.strip().isdigit()
    ]
else:
    GROUP_ROLL_CALL_USER_IDS = sorted(
        set(ALLOWED_USERS) | set(TASK_DISPATCH_NOTIFY_USER_IDS)
    )

# 群聊触发又初回复：@本 bot 之外，@主人 UID / @tgbot 等也算「点名」
GROUP_REPLY_MENTIONS = [
    x.strip().lower().lstrip('@')
    for x in os.getenv('GROUP_REPLY_MENTIONS', 'tgbot,youchu_ai_bot,youchu8888').split(',')
    if x.strip()
]
_reply_mention_uid_raw = os.getenv('GROUP_REPLY_MENTION_USER_IDS', '').strip()
if _reply_mention_uid_raw:
    GROUP_REPLY_MENTION_USER_IDS = [
        int(x) for x in _reply_mention_uid_raw.split(',') if x.strip().isdigit()
    ]
else:
    GROUP_REPLY_MENTION_USER_IDS = sorted(
        set(ALLOWED_USERS) | set(TASK_DISPATCH_NOTIFY_USER_IDS)
    )
