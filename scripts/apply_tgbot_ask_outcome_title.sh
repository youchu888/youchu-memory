#!/usr/bin/env bash
# old-mac：TG「问狂人」超时勿标「狂人回复」补丁（memory sync 后执行）
# 用法：
#   bash ~/.dc-platform/memory/scripts/apply_tgbot_ask_outcome_title.sh
#   TGBOT_DIR=/path/to/omdb/tgbot bash ~/.dc-platform/memory/scripts/apply_tgbot_ask_outcome_title.sh
set -euo pipefail

MEMORY_ROOT="${MEMORY_ROOT:-$HOME/.dc-platform/memory}"
PATCH_DIR="${PATCH_DIR:-$MEMORY_ROOT/patches/tgbot-ask-outcome-title}"
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${TGBOT_DIR}/.bak_ask_outcome_title_${STAMP}"

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "[fail] patch dir missing: $PATCH_DIR" >&2
  echo "先 memory sync，确认 patches/tgbot-ask-outcome-title 已拉到本机。" >&2
  exit 1
fi
if [[ ! -d "$TGBOT_DIR" ]]; then
  echo "[fail] tgbot dir missing: $TGBOT_DIR" >&2
  exit 1
fi

echo "[info] patch=$PATCH_DIR"
echo "[info] target=$TGBOT_DIR"
echo "[info] backup=$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

FILES=(direct_commands.py worker_ant_bus.py)
for f in "${FILES[@]}"; do
  if [[ ! -f "$PATCH_DIR/$f" ]]; then
    echo "[fail] missing patch file: $f" >&2
    exit 1
  fi
  if [[ -f "$TGBOT_DIR/$f" ]]; then
    cp "$TGBOT_DIR/$f" "$BACKUP_DIR/$f"
  fi
  cp "$PATCH_DIR/$f" "$TGBOT_DIR/$f"
  echo "[ok] installed $f"
done

rm -f "$TGBOT_DIR"/__pycache__/direct_commands*.pyc \
  "$TGBOT_DIR"/__pycache__/worker_ant_bus*.pyc 2>/dev/null || true

PYTHON=python3
if [[ -x "$TGBOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$TGBOT_DIR/.venv/bin/python"
fi

"$PYTHON" - <<PY
import sys
sys.path.insert(0, r'''$TGBOT_DIR''')
from worker_ant_bus import ask_outcome_title
pending = '已通过 agent-bus 发给工作狂人（bus id=7734）。等待 120s 内未收到实质回复，狂人回话后会私聊通知你。'
assert ask_outcome_title(pending) == '已转问狂人', ask_outcome_title(pending)
assert ask_outcome_title('【GO】可以跑 test') == '狂人回复'
print('[ok] ask_outcome_title smoke')
PY

if [[ -x "$TGBOT_DIR/restart.sh" ]]; then
  bash "$TGBOT_DIR/restart.sh"
  echo "[ok] restart done"
else
  echo "[warn] restart.sh missing — 请手动重启 bot"
fi

echo "[done] TG ask_outcome_title patch applied."
