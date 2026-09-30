#!/usr/bin/env bash
# 新 Mac 开发机：停掉本机全部自动化 LaunchAgent，交回 old-mac 跑。
# 对称于 enable-automation-as-authority-new-mac.sh
set -euo pipefail

DOMAIN="gui/$(id -u)"
DISABLED="$HOME/Library/LaunchAgents/disabled-on-new-mac"
AUTH_FILE="$HOME/.dc-platform/memory/work-log/AUTHORITY_HOST"
HOST_ENV="$HOME/.dc-platform/memory/.env.host"
mkdir -p "$DISABLED"

# 必须先停保活巡检，否则会把下面的服务再拉起来
ENSURE_FIRST=(com.youchu.automation-ensure)

LABELS=(
  com.youchu.automation-ensure
  com.youchu.agent-bus-poller
  com.dc.tgbot-daemon
  com.youchu.tgbot-dc
  com.youchu.vpn-sync
  com.youchu.onehr-checkin
  com.youchu.ethan-jobs-watch
  com.youchu.memory-git-sync
  com.youchu.chcode-git-sync
  com.youchu.daily-report-wake
  com.youchu.daily-report-fallback
  com.youchu.worker-ant-daily-learn
  com.youchu.memory-daily-light-tidy
  com.youchu.pre-daily-report-flush
)

echo "=== 1) 停 automation-ensure ==="
for label in "${ENSURE_FIRST[@]}"; do
  launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
  launchctl disable "$DOMAIN/$label" 2>/dev/null || true
done

echo "=== 2) bootout 全部自动化 ==="
for label in "${LABELS[@]}"; do
  launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
  launchctl disable "$DOMAIN/$label" 2>/dev/null || true
done

echo "=== 3) 杀残留进程 ==="
pkill -f "agent_bus_poll.py" 2>/dev/null || true
pkill -f "start-agent-bus-daemon.sh" 2>/dev/null || true
pkill -f "wake-bridge" 2>/dev/null || true
pkill -f "Application Support/tgbot-dc" 2>/dev/null || true
pkill -f "tgbot-dc/runtime/bot.py" 2>/dev/null || true
pkill -f "onehr_checkin_scheduler.py" 2>/dev/null || true
pkill -f "ethan_channel_bigdata_jobs.py" 2>/dev/null || true
# 本机临时隧道（test 平台），不交给 LaunchAgent 管也一并收掉
pkill -f "ssh .*13306" 2>/dev/null || true
pkill -f "ssh .*18012" 2>/dev/null || true
pkill -f "ensure-test-platform-tunnels" 2>/dev/null || true

echo "=== 4) plist 挪到 disabled-on-new-mac ==="
for label in "${LABELS[@]}"; do
  src="$HOME/Library/LaunchAgents/${label}.plist"
  if [[ -f "$src" ]]; then
    mv -f "$src" "$DISABLED/${label}.plist"
    echo "  moved $label"
  fi
done

echo "=== 5) 权威主机 → old-mac + 禁本机自动化标记 ==="
cat >"$AUTH_FILE" <<'EOF'
# 正式日报权威主机（一行，勿加引号）
# 2026-09-30：自动化交回 old-mac；new-mac 仅开发、不跑自动化
old-mac
EOF
printf '%s\n' 'export WORKLOG_HOST_ID=old-mac' >"$HOST_ENV"
mkdir -p "$HOME/.dc-platform/config"
# sync-memory-git / ensure-automation 见到此文件则不重装本机 LaunchAgent
cat >"$HOME/.dc-platform/config/DISABLE_LOCAL_AUTOMATION" <<'EOF'
# 本机（new-mac）不跑自动化，交由 old-mac。
# 删掉本文件并跑 enable-automation-as-authority-new-mac.sh 可恢复。
1
EOF
echo "  AUTHORITY_HOST=old-mac  WORKLOG_HOST_ID=old-mac"
echo "  marker: ~/.dc-platform/config/DISABLE_LOCAL_AUTOMATION"

echo "=== 6) 自检 ==="
miss=0
for label in "${LABELS[@]}"; do
  if launchctl print "$DOMAIN/$label" >/dev/null 2>&1; then
    echo "  STILL LOADED  $label"
    miss=1
  else
    echo "  OK stopped    $label"
  fi
done
alive="$(pgrep -lf 'agent_bus_poll|tgbot-dc/runtime/bot|onehr_checkin_scheduler|ethan_channel_bigdata' 2>/dev/null || true)"
if [[ -n "$alive" ]]; then
  echo "  WARN 残留进程:"
  echo "$alive" | sed 's/^/    /'
  miss=1
fi

echo "=== DONE authority=old-mac ==="
echo "plist 备份: $DISABLED"
echo "请在 old-mac 确认 bot / agent-bus / onehr / vpn / memory-sync 等仍在跑。"
exit "$miss"
