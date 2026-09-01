#!/usr/bin/env bash
# OneHR 考勤 · 截取 Telegram「设备管理」页
#
# 用法：
#   onehr_telegram_devices_screenshot.sh          # 打开设置→设备管理后截图
#   onehr_telegram_devices_screenshot.sh --capture-only   # 只截当前 Telegram 窗口
#   onehr_telegram_devices_screenshot.sh --skip-validate  # 跳过内容校验（调试用）
#
# 必须截到「设置侧栏 + 登录设备管理」整页；禁止左边仍是聊天列表的 overlay 态。
# 窗口定位走 CoreGraphics（不依赖 System Events，避免 launchd AppleEvent 超时后误传旧图）
# 输出：~/Desktop/CH/telegram/telegram_devices_YYYYMMDD_HHMMSS.png

set -euo pipefail

CAPTURE_ONLY=false
SKIP_VALIDATE=false
for arg in "$@"; do
  case "$arg" in
    --capture-only) CAPTURE_ONLY=true ;;
    --skip-validate) SKIP_VALIDATE=true ;;
  esac
done

TG_APP="${TELEGRAM_APP:-Telegram}"
OUT_DIR="${ONEHR_SCREENSHOT_DIR:-$HOME/Desktop/CH/telegram}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SRC="$SCRIPT_DIR/onehr_tg_window_info.swift"
HELPER_BIN="$SCRIPT_DIR/onehr_tg_window_info"
VALIDATE_SRC="$SCRIPT_DIR/onehr_tg_screenshot_validate.swift"
VALIDATE_BIN="$SCRIPT_DIR/onehr_tg_screenshot_validate"
mkdir -p "$OUT_DIR"

timestamp="$(date +%Y%m%d_%H%M%S)"
outfile="$OUT_DIR/telegram_devices_${timestamp}.png"

if [[ ! -d "/Applications/${TG_APP}.app" ]]; then
  echo "ERROR: 未找到 /Applications/${TG_APP}.app" >&2
  exit 1
fi

ensure_bin() {
  local src="$1" bin="$2"
  if [[ ! -f "$src" ]]; then
    echo "ERROR: 缺少 $src" >&2
    return 1
  fi
  if [[ ! -x "$bin" || "$src" -nt "$bin" ]]; then
    /usr/bin/swiftc -O -o "$bin" "$src"
  fi
}

capture_once() {
  ensure_bin "$HELPER_SRC" "$HELPER_BIN"
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
    return 1
  fi

  if ! /usr/sbin/screencapture -x -l"$wid" "$outfile" 2>/dev/null; then
    /usr/sbin/screencapture -x "-R${x},${y},${w},${h}" "$outfile"
  fi

  if [[ ! -s "$outfile" ]]; then
    echo "ERROR: 截图失败 $outfile" >&2
    return 1
  fi
  echo "  window_id=${wid} region: x=${x} y=${y} w=${w} h=${h}"
}

navigate_settings_devices() {
  # 必须先进入完整「设置」，再进设备管理。
  # 直接 tg://settings/devices 或 privacy→devices 往返，容易变成「左聊天 + 右设备页」overlay。
  open "tg://settings" >/dev/null 2>&1 || true
  sleep 1.8
  open "tg://settings/devices" >/dev/null 2>&1 || true
  sleep 1.5
  open "tg://settings/devices" >/dev/null 2>&1 || true
  sleep 2.5
  osascript -e "tell application \"$TG_APP\" to activate" >/dev/null 2>&1 || true
  sleep 0.5
}

# 前置到前台，避免截到后台错窗
osascript -e "tell application \"$TG_APP\" to activate" >/dev/null 2>&1 || true
open -a "$TG_APP" >/dev/null 2>&1 || true
sleep 0.8

nav_info=""
if [[ "$CAPTURE_ONLY" != true ]]; then
  navigate_settings_devices
  nav_info="settings→devices×2"
fi

if ! capture_once; then
  exit 1
fi

if [[ "$SKIP_VALIDATE" != true ]]; then
  ensure_bin "$VALIDATE_SRC" "$VALIDATE_BIN"
  if ! validate_out="$("$VALIDATE_BIN" "$outfile" 2>&1)"; then
    # 常见：第一次仍在聊天 overlay，再导航一次重截
    if [[ "$CAPTURE_ONLY" != true ]]; then
      echo "  validate retry: $validate_out" >&2
      rm -f "$outfile"
      navigate_settings_devices
      nav_info="settings→devices×2(retry)"
      timestamp="$(date +%Y%m%d_%H%M%S)"
      outfile="$OUT_DIR/telegram_devices_${timestamp}.png"
      capture_once || exit 1
      if validate_out="$("$VALIDATE_BIN" "$outfile" 2>&1)"; then
        echo "  validate: $validate_out"
      else
        echo "ERROR: 截图内容不是设置→设备管理页，已删除坏图" >&2
        echo "  validate: $validate_out" >&2
        rm -f "$outfile"
        exit 3
      fi
    else
      echo "ERROR: 截图内容不是设置→设备管理页，已删除坏图" >&2
      echo "  validate: $validate_out" >&2
      rm -f "$outfile"
      exit 3
    fi
  else
    echo "  validate: $validate_out"
  fi
fi

echo "OK $outfile"
if [[ -n "$nav_info" ]]; then
  echo "  navigate: ${nav_info}"
fi
