#!/usr/bin/env bash
# OneHR 考勤 · 截取 Telegram「设备管理」页
#
# 用法：
#   onehr_telegram_devices_screenshot.sh          # 刷新会话列表后截「设置→设备管理」
#   onehr_telegram_devices_screenshot.sh --capture-only   # 只截当前 Telegram 窗口
#   onehr_telegram_devices_screenshot.sh --skip-validate  # 跳过内容校验（调试用）
#   onehr_telegram_devices_screenshot.sh --skip-refresh   # 不切账号刷新（仅导航）
#
# 刷新：又初 → Ethan → 又初（Window 菜单 AX 点击），再进设置→设备管理。
# 必须截到「设置侧栏 + 登录设备管理」且账号为又初；禁止左聊天 overlay / Ethan 页。
# 输出：~/Desktop/CH/telegram/telegram_devices_YYYYMMDD_HHMMSS.png

set -euo pipefail

CAPTURE_ONLY=false
SKIP_VALIDATE=false
SKIP_REFRESH=false
for arg in "$@"; do
  case "$arg" in
    --capture-only) CAPTURE_ONLY=true ;;
    --skip-validate) SKIP_VALIDATE=true ;;
    --skip-refresh) SKIP_REFRESH=true ;;
  esac
done

TG_APP="${TELEGRAM_APP:-Telegram}"
OUT_DIR="${ONEHR_SCREENSHOT_DIR:-$HOME/Desktop/CH/telegram}"
PRIMARY_ACCOUNT="${ONEHR_TG_PRIMARY_ACCOUNT:-又初}"
BOUNCE_ACCOUNT="${ONEHR_TG_BOUNCE_ACCOUNT:-Ethan}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_SRC="$SCRIPT_DIR/onehr_tg_window_info.swift"
HELPER_BIN="$SCRIPT_DIR/onehr_tg_window_info"
VALIDATE_SRC="$SCRIPT_DIR/onehr_tg_screenshot_validate.swift"
VALIDATE_BIN="$SCRIPT_DIR/onehr_tg_screenshot_validate"
CLICK_SRC="$SCRIPT_DIR/onehr_tg_click_account.swift"
CLICK_BIN="$SCRIPT_DIR/onehr_tg_click_account"
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

click_account() {
  local name="$1"
  ensure_bin "$CLICK_SRC" "$CLICK_BIN"
  "$CLICK_BIN" "$name"
}

refresh_via_account_bounce() {
  # 切到副号再切回主号，逼 Desktop 重拉「其他设备」列表
  echo "  refresh: ${PRIMARY_ACCOUNT} → ${BOUNCE_ACCOUNT} → ${PRIMARY_ACCOUNT}"
  open "tg://settings" >/dev/null 2>&1 || true
  sleep 1.2
  osascript -e "tell application \"$TG_APP\" to activate" >/dev/null 2>&1 || true
  sleep 0.3
  click_account "$BOUNCE_ACCOUNT"
  sleep 2.5
  click_account "$PRIMARY_ACCOUNT"
  sleep 2.5
}

navigate_settings_devices() {
  # 必须先进入完整「设置」，再进设备管理。
  open "tg://settings" >/dev/null 2>&1 || true
  sleep 1.5
  open "tg://settings/devices" >/dev/null 2>&1 || true
  sleep 1.5
  open "tg://settings/devices" >/dev/null 2>&1 || true
  sleep 2.5
  osascript -e "tell application \"$TG_APP\" to activate" >/dev/null 2>&1 || true
  sleep 0.5
}

# 前置到前台
osascript -e "tell application \"$TG_APP\" to activate" >/dev/null 2>&1 || true
open -a "$TG_APP" >/dev/null 2>&1 || true
sleep 0.8

nav_info=""
if [[ "$CAPTURE_ONLY" != true ]]; then
  if [[ "$SKIP_REFRESH" != true ]]; then
    refresh_via_account_bounce
    nav_info="bounce:${BOUNCE_ACCOUNT}→${PRIMARY_ACCOUNT};settings→devices×2"
  else
    nav_info="settings→devices×2"
  fi
  navigate_settings_devices
fi

if ! capture_once; then
  exit 1
fi

if [[ "$SKIP_VALIDATE" != true ]]; then
  ensure_bin "$VALIDATE_SRC" "$VALIDATE_BIN"
  if ! validate_out="$("$VALIDATE_BIN" "$outfile" 2>&1)"; then
    if [[ "$CAPTURE_ONLY" != true ]]; then
      echo "  validate retry: $validate_out" >&2
      rm -f "$outfile"
      # 重试时再做一次往返，确保切回主号
      if [[ "$SKIP_REFRESH" != true ]]; then
        refresh_via_account_bounce || true
      fi
      navigate_settings_devices
      nav_info="${nav_info};retry"
      timestamp="$(date +%Y%m%d_%H%M%S)"
      outfile="$OUT_DIR/telegram_devices_${timestamp}.png"
      capture_once || exit 1
      if validate_out="$("$VALIDATE_BIN" "$outfile" 2>&1)"; then
        echo "  validate: $validate_out"
      else
        echo "ERROR: 截图内容不是又初的设置→设备管理页，已删除坏图" >&2
        echo "  validate: $validate_out" >&2
        rm -f "$outfile"
        exit 3
      fi
    else
      echo "ERROR: 截图内容不是又初的设置→设备管理页，已删除坏图" >&2
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
