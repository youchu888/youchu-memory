#!/usr/bin/env bash
# new-mac：停掉本机 TG bot，不再抢 getUpdates；权威交回 old-mac。
# 保留 memory-git-sync（个人仓同步仍要跑）。
# 用法：bash ~/.dc-platform/memory/patches/tgbot-dm-cursor-agent-restore/release-bot-on-new-mac.sh
set -euo pipefail

DOMAIN="gui/$(id -u)"
DISABLED="$HOME/Library/LaunchAgents/disabled-on-new-mac"
AUTH_FILE="$HOME/.dc-platform/memory/work-log/AUTHORITY_HOST"
HOST_ENV="$HOME/.dc-platform/memory/.env.host"
ROLE_FILE="$HOME/.dc-platform/tgbot-role"
mkdir -p "$DISABLED" "$HOME/.dc-platform/config" "$(dirname "$AUTH_FILE")"

BOT_LABELS=(
  com.youchu.automation-ensure
  com.dc.tgbot-daemon
  com.youchu.tgbot-dc
)

echo "=== 1) 停保活 + TG bot LaunchAgent ==="
for label in "${BOT_LABELS[@]}"; do
  launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
  launchctl disable "$DOMAIN/$label" 2>/dev/null || true
  src="$HOME/Library/LaunchAgents/${label}.plist"
  if [[ -f "$src" ]]; then
    mv -f "$src" "$DISABLED/${label}.plist"
    echo "  moved $label"
  fi
done

echo "=== 2) 杀 bot 残留 ==="
pkill -f "tgbot-dc/runtime/bot.py" 2>/dev/null || true
pkill -f "Application Support/tgbot-dc" 2>/dev/null || true
pkill -f "omdb/tgbot/bot.py" 2>/dev/null || true
rm -f /tmp/tgbot-dc.pid /tmp/tgbot-dc-daemon.pid /tmp/tgbot-dc.heartbeat 2>/dev/null || true
sleep 1

echo "=== 3) 角色 auxiliary + 权威 old-mac ==="
printf 'auxiliary\n' >"$ROLE_FILE"
cat >"$AUTH_FILE" <<'EOF'
# 正式日报权威主机（一行，勿加引号）
# 2026-11-23：TG bot 交回 old-mac；new-mac 不起 bot（不抢 token）
old-mac
EOF
printf '%s\n' 'export WORKLOG_HOST_ID=old-mac' >"$HOST_ENV"

# 仅标记「本机不起自动化保活」；memory-git-sync 保持
cat >"$HOME/.dc-platform/config/DISABLE_LOCAL_AUTOMATION" <<'EOF'
# 本机（new-mac）不起 TG bot / 自动化保活，交由 old-mac。
# 删掉本文件并跑 enable-automation-as-authority-new-mac.sh 可再接管。
1
EOF

echo "=== 4) 自检 ==="
if pgrep -lf 'tgbot-dc/runtime/bot.py|omdb/tgbot/bot.py' >/dev/null 2>&1; then
  echo "  WARN bot 进程仍在" >&2
  pgrep -lf 'tgbot-dc/runtime/bot.py|omdb/tgbot/bot.py' || true
  exit 1
fi
echo "  role=$(tr -d ' \n' <"$ROLE_FILE")"
echo "  authority=$(grep -v '^#' "$AUTH_FILE" | head -1)"
echo "  OK new-mac 已停抢；请在 old-mac 跑 reclaim-bot-on-old-mac.sh"
