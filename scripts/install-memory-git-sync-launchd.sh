#!/usr/bin/env bash
# 安装 launchd：定时 git 同步 ~/.dc-platform/memory
#
# 优先读仓内 config/memory_sync.env（MODE / INTERVAL_SEC / HOUR / MINUTE）
# 环境变量可覆盖：MEMORY_SYNC_MODE / INTERVAL_SEC / MEMORY_SYNC_HOUR / MEMORY_SYNC_MINUTE
#
# 单机（old-mac 停）：MODE=daily，默认 22:30
# 双机恢复：MODE=interval（或 MEMORY_SYNC_MODE=interval）
set -euo pipefail
LABEL=com.youchu.memory-git-sync
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
HERE="$(cd "$(dirname "$0")" && pwd)"
STD_DIR="$HOME/.dc-platform/scripts"
LOG_DIR="$HOME/.dc-platform/logs"
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
CFG="$MEM/config/memory_sync.env"

_cfg_get() {
  local key="$1" def="$2" v=""
  if [[ -f "$CFG" ]]; then
    v="$(grep -E "^[[:space:]]*${key}=" "$CFG" | tail -1 | cut -d= -f2- | tr -d '[:space:]' || true)"
  fi
  [[ -n "$v" ]] && echo "$v" || echo "$def"
}

MODE="${MEMORY_SYNC_MODE:-$(_cfg_get MODE daily)}"
INTERVAL_SEC="${INTERVAL_SEC:-$(_cfg_get INTERVAL_SEC 120)}"
HOUR="${MEMORY_SYNC_HOUR:-$(_cfg_get MEMORY_SYNC_HOUR 22)}"
MINUTE="${MEMORY_SYNC_MINUTE:-$(_cfg_get MEMORY_SYNC_MINUTE 30)}"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$STD_DIR"
chmod +x "$HERE"/sync-memory-git.sh "$HERE"/install-memory-git-sync-launchd.sh "$HERE"/uninstall-memory-git-sync-launchd.sh 2>/dev/null || true
chmod +x "$HERE"/worklog_dual_mac_sync.py "$HERE"/export_noncode_mirrors.py 2>/dev/null || true
if [[ "$(cd "$HERE" && pwd)" != "$(cd "$STD_DIR" && pwd)" ]]; then
  cp -f "$HERE"/sync-memory-git.sh "$HERE"/install-memory-git-sync-launchd.sh "$HERE"/uninstall-memory-git-sync-launchd.sh "$STD_DIR/" 2>/dev/null || true
  cp -f "$HERE"/worklog_dual_mac_sync.py "$HERE"/export_noncode_mirrors.py "$STD_DIR/" 2>/dev/null || true
fi
chmod +x "$STD_DIR"/sync-memory-git.sh "$STD_DIR"/install-memory-git-sync-launchd.sh "$STD_DIR"/uninstall-memory-git-sync-launchd.sh 2>/dev/null || true
chmod +x "$STD_DIR"/export_noncode_mirrors.py 2>/dev/null || true
SCRIPT="$STD_DIR/sync-memory-git.sh"

if [[ "$MODE" == "interval" ]]; then
  SCHEDULE_XML="  <key>StartInterval</key><integer>${INTERVAL_SEC}</integer>"
  SCHEDULE_MSG="每 ${INTERVAL_SEC} 秒（双机高频）"
else
  SCHEDULE_XML=$(cat <<EOF
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>${HOUR}</integer>
    <key>Minute</key><integer>${MINUTE}</integer>
  </dict>
EOF
)
  SCHEDULE_MSG="每天 $(printf '%02d:%02d' "$HOUR" "$MINUTE") Asia/Shanghai（单机下班同步）"
fi

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0 //EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${SCRIPT}</string>
  </array>
${SCHEDULE_XML}
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>${LOG_DIR}/memory-git-sync.log</string>
  <key>StandardErrorPath</key><string>${LOG_DIR}/memory-git-sync.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin</string>
    <key>HOME</key><string>${HOME}</string>
    <key>TZ</key><string>Asia/Shanghai</string>
  </dict>
</dict>
</plist>
EOF

DOMAIN="gui/$(id -u)"
launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
launchctl unload "$PLIST" 2>/dev/null || true
if ! launchctl bootstrap "$DOMAIN" "$PLIST" 2>/dev/null; then
  launchctl load -w "$PLIST" 2>/dev/null || launchctl bootstrap "$DOMAIN" "$PLIST"
fi
launchctl enable "${DOMAIN}/${LABEL}" 2>/dev/null || true
echo "✓ 已安装 ${LABEL}：${SCHEDULE_MSG}"
echo "  脚本：$SCRIPT"
echo "  日志：${LOG_DIR}/memory-git-sync.log"
echo "  双机恢复：把 config/memory_sync.env 的 MODE=interval，再跑一次 sync"
echo "  卸载：bash ${STD_DIR}/uninstall-memory-git-sync-launchd.sh"
