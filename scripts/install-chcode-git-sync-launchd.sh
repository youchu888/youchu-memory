#!/usr/bin/env bash
# 安装每天自动拉取 CHcode（默认 08:30 Asia/Shanghai）
# 环境变量可选：CHCODE_ROOT / CHCODE_BRANCH / CHCODE_SYNC_HOUR / CHCODE_SYNC_MINUTE
set -euo pipefail

LABEL="com.youchu.chcode-git-sync"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
STD_DIR="$HOME/.dc-platform/scripts"
LOG_DIR="$HOME/.dc-platform/logs"
SCRIPT="$STD_DIR/sync-chcode-git.sh"
HERE="$(cd "$(dirname "$0")" && pwd)"
DOMAIN="gui/$(id -u)"
HOUR="${CHCODE_SYNC_HOUR:-8}"
MINUTE="${CHCODE_SYNC_MINUTE:-30}"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$STD_DIR"

# 安装源可能就是 STD_DIR，避免 cp 自身报错
if [[ "$(cd "$HERE" && pwd)" != "$(cd "$STD_DIR" && pwd)" ]]; then
  cp -f "$HERE/sync-chcode-git.sh" "$SCRIPT"
  cp -f "$HERE/install-chcode-git-sync-launchd.sh" "$STD_DIR/" 2>/dev/null || true
  [[ -f "$HERE/uninstall-chcode-git-sync-launchd.sh" ]] && cp -f "$HERE/uninstall-chcode-git-sync-launchd.sh" "$STD_DIR/"
fi
chmod +x "$SCRIPT" \
  "$STD_DIR/install-chcode-git-sync-launchd.sh" \
  "$STD_DIR/uninstall-chcode-git-sync-launchd.sh" 2>/dev/null || true

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
    <string>${SCRIPT}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>${HOUR}</integer>
    <key>Minute</key>
    <integer>${MINUTE}</integer>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_DIR}/chcode-git-sync.launchd.stdout.log</string>
  <key>StandardErrorPath</key>
  <string>${LOG_DIR}/chcode-git-sync.launchd.stderr.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>${HOME}</string>
    <key>TZ</key>
    <string>Asia/Shanghai</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin</string>
    <key>CHCODE_ROOT</key>
    <string>${HOME}/Desktop/CHcode</string>
    <key>CHCODE_BRANCH</key>
    <string>dev</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"
launchctl enable "${DOMAIN}/${LABEL}" 2>/dev/null || true
launchctl kickstart "${DOMAIN}/${LABEL}" 2>/dev/null || true

echo "OK 已安装 ${LABEL}"
echo "  每天 ${HOUR}:$(printf '%02d' "$MINUTE")（Asia/Shanghai）拉取 CHcode/dev"
echo "  脚本: $SCRIPT"
echo "  日志: ${LOG_DIR}/chcode-git-sync.log"
echo "  卸载: bash ${STD_DIR}/uninstall-chcode-git-sync-launchd.sh"
