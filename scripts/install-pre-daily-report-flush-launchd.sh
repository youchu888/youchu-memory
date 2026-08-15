#!/usr/bin/env bash
# 双机都装：冲刺上传当日任务到 youchu-memory（写日报之前）
# 主人 2026-08-15：周一至周五 21:20；周六 18:20（Asia/Shanghai）
set -euo pipefail

# launchd Weekday: 1=Mon … 6=Sat
calendar_intervals() {
  local h_wd="$1" m_wd="$2" h_sat="$3" m_sat="$4" wd
  printf '  <key>StartCalendarInterval</key>\n  <array>\n'
  for wd in 1 2 3 4 5; do
    printf '    <dict>\n      <key>Weekday</key>\n      <integer>%s</integer>\n      <key>Hour</key>\n      <integer>%s</integer>\n      <key>Minute</key>\n      <integer>%s</integer>\n    </dict>\n' "$wd" "$h_wd" "$m_wd"
  done
  printf '    <dict>\n      <key>Weekday</key>\n      <integer>6</integer>\n      <key>Hour</key>\n      <integer>%s</integer>\n      <key>Minute</key>\n      <integer>%s</integer>\n    </dict>\n  </array>\n' "$h_sat" "$m_sat"
}

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
$(calendar_intervals 21 20 18 20)
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

echo "[install] ${LABEL} @Mon–Fri 21:20 / Sat 18:20 Asia/Shanghai plist=$PLIST"
echo "[install] 新 Mac / 旧 Mac 都要跑本安装脚本一次"
echo "[note] CHCODE_ROOT unused; ROOT=$ROOT"
