#!/usr/bin/env bash
# 安装 launchd：定时 git 同步 ~/.dc-platform/memory（两台各装一份，互相协调）
# 间隔：环境变量 INTERVAL_SEC（默认 600 秒 = 10 分钟）
set -euo pipefail
LABEL=com.youchu.memory-git-sync
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/sync-memory-git.sh"
# 同时落到标准位置，方便手动调用
STD_DIR="$HOME/.dc-platform/scripts"
LOG_DIR="$HOME/.dc-platform/logs"
INTERVAL_SEC="${INTERVAL_SEC:-600}"
mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$STD_DIR"
chmod +x "$HERE"/sync-memory-git.sh "$HERE"/install-memory-git-sync-launchd.sh "$HERE"/uninstall-memory-git-sync-launchd.sh 2>/dev/null || true
cp -f "$HERE"/sync-memory-git.sh "$HERE"/install-memory-git-sync-launchd.sh "$HERE"/uninstall-memory-git-sync-launchd.sh "$STD_DIR/"
chmod +x "$STD_DIR"/sync-memory-git.sh "$STD_DIR"/install-memory-git-sync-launchd.sh "$STD_DIR"/uninstall-memory-git-sync-launchd.sh
# plist 指向标准位置（稳定路径）
SCRIPT="$STD_DIR/sync-memory-git.sh"

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
  <key>StartInterval</key><integer>${INTERVAL_SEC}</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>${LOG_DIR}/memory-git-sync.log</string>
  <key>StandardErrorPath</key><string>${LOG_DIR}/memory-git-sync.err.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin</string>
    <key>HOME</key><string>${HOME}</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl kickstart "gui/$(id -u)/${LABEL}" 2>/dev/null || true
echo "✓ 已安装 ${LABEL}（每 ${INTERVAL_SEC} 秒）"
echo "  脚本：$SCRIPT"
echo "  日志：${LOG_DIR}/memory-git-sync.log"
echo "  卸载：bash ${STD_DIR}/uninstall-memory-git-sync-launchd.sh"
