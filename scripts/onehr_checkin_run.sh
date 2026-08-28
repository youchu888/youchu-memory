#!/usr/bin/env bash
# OneHR 考勤一键：Telegram 截图 → 检测开放时段 → 上传打卡
#
# 用法：
#   onehr_checkin_run.sh              # 正常执行
#   onehr_checkin_run.sh --dry-run    # 只检测，不截图不上传
#   onehr_checkin_run.sh --capture-only

set -euo pipefail

ENV_FILE="${ONEHR_ENV:-$HOME/.dc-platform/config/onehr.env}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${ONEHR_PYTHON:-$(command -v python3)}"
AUTO_PY="$SCRIPT_DIR/onehr_checkin_auto.py"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: 缺少 $ENV_FILE（可复制 onehr.env.example）" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

export ONEHR_SCREENSHOT_DIR="${ONEHR_SCREENSHOT_DIR:-$HOME/Desktop/CH/telegram}"
export ONEHR_SCREENSHOT_SCRIPT="${ONEHR_SCREENSHOT_SCRIPT:-$SCRIPT_DIR/onehr_telegram_devices_screenshot.sh}"

exec "$PYTHON" -u "$AUTO_PY" --env "$ENV_FILE" "$@"
