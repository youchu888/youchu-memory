#!/bin/bash
# 每天 02:00（上海）读上一自然日的群和私聊，分类沉淀后把汇总推到私聊。
# 学完自动融合已有记忆（memory-fuse-after-tg-learn.sh，由 learn 进程内调用）。
# 不写工作汇报、不进工作簿进展。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TGBOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LABEL="com.youchu.daily-group-learn"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
APP_SUPPORT="$HOME/Library/Application Support/youchu-daily-group-learn"
LAUNCHER="$APP_SUPPORT/run.sh"
LOG_DIR="$HOME/.dc-platform/logs"
LOG_OUT="$LOG_DIR/daily-group-learn.stdout.log"
LOG_ERR="$LOG_DIR/daily-group-learn.stderr.log"
FUSE_SH="$HOME/.dc-platform/scripts/memory-fuse-after-tg-learn.sh"
CANON_LEARN="$HOME/Desktop/CHcode/omdb/tgbot/scripts/daily_group_chat_learn.py"

# shellcheck source=../_env.sh
source "$TGBOT_DIR/_env.sh"
PY="$(tgbot_python)"
LEARN_PY="$TGBOT_DIR/scripts/daily_group_chat_learn.py"

# 与仓内 canonical 对齐（防旧副本）
if [[ -f "$CANON_LEARN" ]]; then
  cp -p "$CANON_LEARN" "$LEARN_PY" 2>/dev/null || true
fi
chmod +x "$FUSE_SH" 2>/dev/null || true

mkdir -p "$APP_SUPPORT" "$LOG_DIR" "$HOME/Library/LaunchAgents"

cat > "$LAUNCHER" <<EOF
#!/bin/bash
set -euo pipefail
export HOME="$HOME"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${HOME}/.local/bin:\${PATH}"
export TZ="Asia/Shanghai"
export WORKSPACE_ROOT="\${WORKSPACE_ROOT:-$HOME/Desktop/CHcode}"
cd "$TGBOT_DIR"
# learn 进程内会调 fuse；此处再兜底一次，防止旧版 learn 没挂钩
"$PY" -u "$LEARN_PY" --yesterday
DAY="\$(TZ=Asia/Shanghai date -v-1d '+%Y-%m-%d' 2>/dev/null || TZ=Asia/Shanghai date -d 'yesterday' '+%Y-%m-%d')"
if [[ -x "$FUSE_SH" || -f "$FUSE_SH" ]]; then
  bash "$FUSE_SH" --day "\$DAY" || true
fi
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
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>2</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>WorkingDirectory</key>
  <string>${TGBOT_DIR}</string>
  <key>StandardOutPath</key>
  <string>${LOG_OUT}</string>
  <key>StandardErrorPath</key>
  <string>${LOG_ERR}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key>
    <string>${HOME}</string>
    <key>TZ</key>
    <string>Asia/Shanghai</string>
  </dict>
</dict>
</plist>
EOF

DOMAIN="gui/$(id -u)"
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST_DST" 2>/dev/null || launchctl load -w "$PLIST_DST"
launchctl enable "$DOMAIN/$LABEL" 2>/dev/null || true
echo "OK installed ${LABEL} 每天 02:00（上一自然日）"
echo "log: ${LOG_OUT}"
