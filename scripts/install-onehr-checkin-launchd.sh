#!/usr/bin/env bash
# 安装 OneHR 调度守护（极客同款：窗口内随机时刻，KeepAlive）
set -euo pipefail

LABEL="com.youchu.onehr-checkin"
ENV_FILE="${ONEHR_ENV:-$HOME/.dc-platform/config/onehr.env}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEDULER_PY="$SCRIPT_DIR/onehr_checkin_scheduler.py"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
APP_SUPPORT="$HOME/Library/Application Support/onehr-checkin"
LAUNCHER="$APP_SUPPORT/run-scheduler.sh"
LOG_DIR="${ONEHR_LOG_DIR:-$HOME/.dc-platform/onehr/logs}"
PYTHON="${ONEHR_PYTHON:-$(command -v python3)}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: 先创建 $ENV_FILE" >&2
  exit 1
fi

mkdir -p "$APP_SUPPORT" "$LOG_DIR" "$HOME/Library/LaunchAgents"
chmod 700 "$APP_SUPPORT"
chmod +x "$SCHEDULER_PY"

cat > "$LAUNCHER" <<EOF
#!/bin/bash
set -euo pipefail
export HOME="$HOME"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export ONEHR_ENV="$ENV_FILE"
LOG="$LOG_DIR/launchd.log"
{
  echo "[\$(date '+%F %T')] onehr-scheduler start"
  exec "$PYTHON" -u "$SCHEDULER_PY" --env "$ENV_FILE"
} >> "\$LOG" 2>&1
EOF
chmod +x "$LAUNCHER"

cat > "$PLIST_DST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${LAUNCHER}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/launchd.stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>${HOME}</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "OK 已安装 ${LABEL}（极客同款随机窗调度）"
echo "  plist: $PLIST_DST"
echo "  查看今日计划: python3 $SCHEDULER_PY --show-plan"
echo "  日志: $LOG_DIR/scheduler.log"
