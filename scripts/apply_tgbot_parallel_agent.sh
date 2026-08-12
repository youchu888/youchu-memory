#!/usr/bin/env bash
# 旧 Mac：把 memory 里的 TG 并行 agent 补丁应用到本机 tgbot 并重启。
# 用法：
#   bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh
#   TGBOT_DIR=/path/to/omdb/tgbot bash ~/.dc-platform/memory/scripts/apply_tgbot_parallel_agent.sh
set -euo pipefail

MEMORY_ROOT="${MEMORY_ROOT:-$HOME/.dc-platform/memory}"
PATCH_DIR="${PATCH_DIR:-$MEMORY_ROOT/patches/tgbot-parallel-agent}"
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${TGBOT_DIR}/.bak_parallel_agent_${STAMP}"

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "[fail] patch dir missing: $PATCH_DIR" >&2
  echo "先 memory sync，确认 patches/tgbot-parallel-agent 已拉到本机。" >&2
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

FILES=(agent_queue.py bot.py prompt_builder.py config.py)
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

ENV_FILE="$TGBOT_DIR/.env"
upsert() {
  local k="$1" v="$2"
  if [[ -f "$ENV_FILE" ]] && grep -q "^${k}=" "$ENV_FILE"; then
    sed -i.bak "s|^${k}=.*|${k}=${v}|" "$ENV_FILE"
  else
    printf '\n%s=%s\n' "$k" "$v" >> "$ENV_FILE"
  fi
}
upsert AGENT_PARALLEL_WHEN_BUSY true
upsert AGENT_MAX_PARALLEL 3
upsert AGENT_MEMORY_REFRESH_ON_SPAWN true
rm -f "${ENV_FILE}.bak"
echo "[ok] .env upsert parallel flags"

rm -f "$TGBOT_DIR"/__pycache__/agent_queue*.pyc \
  "$TGBOT_DIR"/__pycache__/bot*.pyc \
  "$TGBOT_DIR"/__pycache__/prompt_builder*.pyc \
  "$TGBOT_DIR"/__pycache__/config*.pyc 2>/dev/null || true

PYTHON=python3
if [[ -x "$TGBOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$TGBOT_DIR/.venv/bin/python"
fi

"$PYTHON" - <<PY
import sys
sys.path.insert(0, r'''$TGBOT_DIR''')
from agent_queue import is_agent_busy
from config import AGENT_PARALLEL_WHEN_BUSY, AGENT_MAX_PARALLEL
from prompt_builder import build_system_prompt
assert AGENT_PARALLEL_WHEN_BUSY is True
p = build_system_prompt(0, user_question='进度', force_new_agent=True)
assert '记忆冷启动' in p
print('[ok] import smoke', AGENT_MAX_PARALLEL, 'busy=', is_agent_busy())
PY

if [[ -x "$TGBOT_DIR/restart.sh" ]]; then
  bash "$TGBOT_DIR/restart.sh"
  echo "[ok] restart done"
else
  echo "[warn] restart.sh missing — 请手动重启 bot"
fi

echo "[done] TG parallel-agent patch applied. playbook: $MEMORY_ROOT/playbook_tg_dm_parallel_agent.md"
