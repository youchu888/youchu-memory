#!/usr/bin/env bash
# OneHR 考勤 · 截取 Telegram「设备管理」页
#
# 用法：
#   onehr_telegram_devices_screenshot.sh          # deeplink 打开设备管理后截图
#   onehr_telegram_devices_screenshot.sh --capture-only   # 只截当前 Telegram 窗口
#
# 窗口定位走 CoreGraphics（不依赖 System Events，避免 launchd AppleEvent 超时后误传旧图）
# 输出：~/Desktop/CH/telegram/telegram_devices_YYYYMMDD_HHMMSS.png

set -euo pipefail

CAPTURE_ONLY=false
if [[ "${1:-}" == "--capture-only" ]]; then
  CAPTURE_ONLY=true
fi

TG_APP="${TELEGRAM_APP:-Telegram}"
OUT_DIR="${ONEHR_SCREENSHOT_DIR:-$HOME/Desktop/CH/telegram}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SRC="$SCRIPT_DIR/onehr_tg_window_info.swift"
HELPER_BIN="$SCRIPT_DIR/onehr_tg_window_info"
mkdir -p "$OUT_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
outfile="$OUT_DIR/telegram_devices_${timestamp}.png"

if [[ ! -d "/Applications/${TG_APP}.app" ]]; then
  echo "ERROR: 未找到 /Applications/${TG_APP}.app" >&2
  exit 1
fi

ensure_helper() {
  if [[ ! -f "$HELPER_SRC" ]]; then
    echo "ERROR: 缺少 $HELPER_SRC" >&2
    return 1
  fi
  if [[ ! -x "$HELPER_BIN" || "$HELPER_SRC" -nt "$HELPER_BIN" ]]; then
    /usr/bin/swiftc -O -o "$HELPER_BIN" "$HELPER_SRC"
  fi
}

open -a "$TG_APP" >/dev/null 2>&1 || true
sleep 0.5

nav_info=""
if [[ "$CAPTURE_ONLY" != true ]]; then
  open "tg://settings/devices" >/dev/null 2>&1 || true
  nav_info="deeplink:tg://settings/devices"
  sleep 1.8
fi

ensure_helper
info="$("$HELPER_BIN" "$TG_APP")"
wid="${info%%$'\t'*}"
region="${info#*$'\t'}"
pos="${region%%|*}"
sz="${region#*|}"
x="${pos%,*}"
y="${pos#*,}"
w="${sz%,*}"
h="${sz#*,}"

if [[ -z "$wid" || -z "$x" || -z "$y" || -z "$w" || -z "$h" ]]; then
  echo "ERROR: 无法读取 Telegram 窗口（helper 输出: ${info:-empty}）" >&2
  exit 1
fi

# 优先按窗口 ID 截，失败再按区域
if ! /usr/sbin/screencapture -x -l"$wid" "$outfile" 2>/dev/null; then
  /usr/sbin/screencapture -x "-R${x},${y},${w},${h}" "$outfile"
fi

if [[ ! -s "$outfile" ]]; then
  echo "ERROR: 截图失败 $outfile" >&2
  exit 1
fi

echo "OK $outfile"
echo "  window_id=${wid} region: x=${x} y=${y} w=${w} h=${h}"
if [[ -n "$nav_info" ]]; then
  echo "  navigate: ${nav_info}"
fi
