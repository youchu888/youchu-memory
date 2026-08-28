#!/usr/bin/env bash
# OneHR 考勤 · 第 1 步：本机截取 Telegram「设备管理 / 已登录设备」页
#
# 用法：
#   onehr_telegram_devices_screenshot.sh          # 自动打开设置并导航后截图
#   onehr_telegram_devices_screenshot.sh --capture-only   # 仅截当前 Telegram 前台窗口
#
# 依赖：Telegram.app、辅助功能权限（终端 / Cursor / iTerm 需允许控制电脑）
# 输出：~/Desktop/CH/telegram/telegram_devices_YYYYMMDD_HHMMSS.png

set -euo pipefail

CAPTURE_ONLY=false
if [[ "${1:-}" == "--capture-only" ]]; then
  CAPTURE_ONLY=true
fi

TG_APP="${TELEGRAM_APP:-Telegram}"
OUT_DIR="${ONEHR_SCREENSHOT_DIR:-$HOME/Desktop/CH/telegram}"
mkdir -p "$OUT_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
outfile="$OUT_DIR/telegram_devices_${timestamp}.png"

if [[ ! -d "/Applications/${TG_APP}.app" ]]; then
  echo "ERROR: 未找到 /Applications/${TG_APP}.app" >&2
  exit 1
fi

open -a "$TG_APP" >/dev/null 2>&1 || true
sleep 0.8

navigate_and_bounds() {
  osascript <<'APPLESCRIPT'
on windowBounds()
  tell application "System Events"
    tell process "Telegram"
      set frontmost to true
      set pos to position of window 1
      set sz to size of window 1
      return pos & "|" & sz
    end tell
  end tell
end windowBounds

tell application "Telegram" to activate
delay 0.4

if not (CAPTURE_ONLY as boolean) then
  tell application "System Events"
    tell process "Telegram"
      set frontmost to true
      keystroke "," using command down
      delay 1.0
      set {wx, wy} to position of window 1
      set {ww, wh} to size of window 1
      -- 侧栏「设备管理」行：按窗口比例定位（1220x1021 下约 130,440）
      set cx to wx + (ww * 130 / 1220)
      set cy to wy + (wh * 440 / 1021)
      click at {cx, cy}
      delay 1.0
    end tell
  end tell
end if

return my windowBounds()
APPLESCRIPT
}

# 注入 bash 变量到 AppleScript
if [[ "$CAPTURE_ONLY" == true ]]; then
  bounds="$(CAPTURE_ONLY=true osascript <<'APPLESCRIPT'
tell application "Telegram" to activate
delay 0.3
tell application "System Events"
  tell process "Telegram"
    set frontmost to true
    set pos to position of window 1
    set sz to size of window 1
    return (item 1 of pos as text) & "," & (item 2 of pos as text) & "|" & (item 1 of sz as text) & "," & (item 2 of sz as text)
  end tell
end tell
APPLESCRIPT
)"
else
  bounds="$(osascript <<'APPLESCRIPT'
tell application "Telegram" to activate
delay 0.3
tell application "System Events"
  tell process "Telegram"
    set frontmost to true
    keystroke "," using command down
    delay 1.0
    set {wx, wy} to position of window 1
    set {ww, wh} to size of window 1
    set cx to wx + (ww * 130 / 1220)
    set cy to wy + (wh * 440 / 1021)
    click at {cx, cy}
    delay 1.0
    set pos to position of window 1
    set sz to size of window 1
    return (item 1 of pos as text) & "," & (item 2 of pos as text) & "|" & (item 1 of sz as text) & "," & (item 2 of sz as text)
  end tell
end tell
APPLESCRIPT
)"
fi

pos="${bounds%%|*}"
sz="${bounds#*|}"
x="${pos%,*}"
y="${pos#*,}"
w="${sz%,*}"
h="${sz#*,}"

if [[ -z "$x" || -z "$y" || -z "$w" || -z "$h" ]]; then
  echo "ERROR: 无法读取 Telegram 窗口位置（检查辅助功能权限）" >&2
  exit 1
fi

/usr/sbin/screencapture -x "-R${x},${y},${w},${h}" "$outfile"

if [[ ! -s "$outfile" ]]; then
  echo "ERROR: 截图失败 $outfile" >&2
  exit 1
fi

echo "OK $outfile"
echo "  region: x=${x} y=${y} w=${w} h=${h}"
