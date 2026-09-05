#!/usr/bin/env bash
# old-mac：工作簿进展禁秒回 · T-1 实查单条汇报（memory sync 后执行）
# 用法：
#   bash ~/.dc-platform/memory/scripts/apply_tgbot_workbook_no_instant_ack.sh
#   TGBOT_DIR=/path/to/omdb/tgbot bash ~/.dc-platform/memory/scripts/apply_tgbot_workbook_no_instant_ack.sh
set -euo pipefail

MEMORY_ROOT="${MEMORY_ROOT:-$HOME/.dc-platform/memory}"
PATCH_DIR="${PATCH_DIR:-$MEMORY_ROOT/patches/tgbot-workbook-no-instant-ack}"
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${TGBOT_DIR}/.bak_workbook_no_instant_ack_${STAMP}"

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "[fail] patch dir missing: $PATCH_DIR" >&2
  echo "先 memory sync，确认 patches/tgbot-workbook-no-instant-ack 已拉到本机。" >&2
  exit 1
fi
if [[ ! -d "$TGBOT_DIR" ]]; then
  echo "[fail] tgbot dir missing: $TGBOT_DIR" >&2
  exit 1
fi

echo "[info] patch=$PATCH_DIR"
echo "[info] target=$TGBOT_DIR"
echo "[info] backup=$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/scripts" "$BACKUP_DIR/data" "$TGBOT_DIR/scripts" "$TGBOT_DIR/data"

install_one() {
  local rel="$1"
  local src="$PATCH_DIR/$rel"
  local dst="$TGBOT_DIR/$rel"
  if [[ ! -f "$src" ]]; then
    echo "[fail] missing patch file: $rel" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$dst")" "$(dirname "$BACKUP_DIR/$rel")"
  if [[ -f "$dst" ]]; then
    cp "$dst" "$BACKUP_DIR/$rel"
  fi
  cp "$src" "$dst"
  echo "[ok] installed $rel"
}

install_one workbook_progress_service.py
install_one group_workbook_progress_handler.py
install_one scripts/post_workbook_progress_to_group.py
install_one data/workbook_supplemental.json

rm -f "$TGBOT_DIR"/__pycache__/workbook_progress_service*.pyc \
  "$TGBOT_DIR"/__pycache__/group_workbook_progress_handler*.pyc 2>/dev/null || true

# shellcheck source=/dev/null
source "$TGBOT_DIR/_env.sh"
PYTHON="$(tgbot_python)"

"$PYTHON" - <<PY
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, r'''$TGBOT_DIR''')
from workbook_progress_service import build_detailed_reply, build_progress_reply, _report_cutoff_date, LiveSnapshot
from group_workbook_progress_handler import (
    fallback_workbook_template,
    in_daily_fallback_window,
    looks_like_canned_fallback,
    parse_youchu_items,
)
assert build_detailed_reply('x') is None, 'detailed must be disabled'
assert _report_cutoff_date('2026-09-03') == '2026-09-02'
# 真验收：禁止再靠函数签名当「禁秒回已成功」
src = open(r'''$TGBOT_DIR/workbook_progress_service.py''', encoding='utf-8').read()
assert '禁止秒回模板' not in src, 'user-facing slogan 禁止秒回模板 must be gone'
stub = fallback_workbook_template('2026-09-05')
assert parse_youchu_items(stub) == [], 'fallback stub must not inject numbered 又初 items'
assert looks_like_canned_fallback(stub, '2026-09-05')
bj = ZoneInfo('Asia/Shanghai')
assert in_daily_fallback_window(datetime(2026, 9, 5, 9, 1, tzinfo=bj)) is False, '09:01 must not be fallback window'
assert in_daily_fallback_window(datetime(2026, 9, 5, 9, 8, tzinfo=bj)) is True
snap = LiveSnapshot(ts='2026-09-05 12:00:00', cutoff_dt='2026-09-04', elapsed_sec=15)
body = build_progress_reply(stub, snap=snap, workbook_date='2026-09-05') or ''
assert '禁止秒回模板' not in body
assert '原文未进站' in body
print('[ok] workbook no-instant-ack smoke')
PY

if [[ "${FORCE_RESTART:-}" == "1" ]] || [[ "${WORKLOG_HOST_ID:-}" == "old-mac" ]]; then
  if [[ -x "$TGBOT_DIR/restart.sh" ]]; then
    bash "$TGBOT_DIR/restart.sh"
    echo "[ok] restart done (old-mac / FORCE_RESTART)"
  else
    echo "[warn] restart.sh missing — 请手动重启 bot"
  fi
else
  # new-mac 默认只装文件，不启 bot（旧机权威；误启会抢 Telegram session）
  host_id="${WORKLOG_HOST_ID:-}"
  if [[ -z "$host_id" && -f "$HOME/.dc-platform/memory/.env.host" ]]; then
    # shellcheck disable=SC1090
    source "$HOME/.dc-platform/memory/.env.host" || true
    host_id="${WORKLOG_HOST_ID:-}"
  fi
  if [[ "$host_id" == "old-mac" ]]; then
    bash "$TGBOT_DIR/restart.sh"
    echo "[ok] restart done"
  else
    echo "[skip] restart（本机=$host_id；请在旧机执行本脚本以 restart）"
  fi
fi

echo "[done] tgbot workbook no-instant-ack patch applied."
