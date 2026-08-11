#!/usr/bin/env bash
# 双机都装：工作日 21:20 冲刺上传当日任务到 youchu-memory（在 21:30 写日报之前）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# 本脚本可放在 .cursor/scripts 或 memory/scripts
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.youchu.pre-daily-report-flush"
APP_SUPPORT="$HOME/Library/Application Support/youchu-agent-bus"
DEPLOY="$APP_SUPPORT/scripts"
STATE_DIR="$APP_SUPPORT/state"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
RUNNER="$APP_SUPPORT/pre-daily-report-flush-run.sh"
MEM_SCRIPTS="$HOME/.dc-platform/memory/scripts"

mkdir -p "$DEPLOY" "$STATE_DIR" "$HOME/Library/LaunchAgents" "$HOME/.dc-platform/logs"

# 优先用 memory 仓 canonical
if [[ -f "$MEM_SCRIPTS/pre_daily_report_flush.sh" ]]; then
  cp "$MEM_SCRIPTS/pre_daily_report_flush.sh" "$DEPLOY/pre_daily_report_flush.sh"
elif [[ -f "$SRC_DIR/pre_daily_report_flush.sh" ]]; then
  cp "$SRC_DIR/pre_daily_report_flush.sh" "$DEPLOY/pre_daily_report_flush.sh"
else
  echo "missing pre_daily_report_flush.sh" >&2
  exit 1
fi
chmod +x "$DEPLOY/pre_daily_report_flush.sh"

cat >"$RUNNER" <<EOF
#!/bin/bash
set -euo pipefail
export HOME="$HOME"
export TZ=Asia/Shanghai
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin"
exec bash "$DEPLOY/pre_daily_report_flush.sh"
EOF
chmod +x "$RUNNER"

cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${RUNNER}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>21</integer>
    <key>Minute</key>
    <integer>20</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
  <key>WorkingDirectory</key>
  <string>${HOME}/.dc-platform</string>
  <key>StandardOutPath</key>
  <string>${HOME}/.dc-platform/logs/pre-daily-report-flush.launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${HOME}/.dc-platform/logs/pre-daily-report-flush.launchd.stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>${HOME}</string>
    <key>TZ</key>
    <string>Asia/Shanghai</string>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${HOME}/.local/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "[install] ${LABEL} @21:20 Asia/Shanghai plist=$PLIST"
echo "[install] 新 Mac / 旧 Mac 都要跑本安装脚本一次"
echo "[note] CHCODE_ROOT unused; ROOT=$ROOT"
