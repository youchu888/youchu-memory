#!/usr/bin/env bash
# 私聊回写修复：默认走 Bot CLI（cursor_agent），禁止只叫醒 IDE 不回 TG。
# 用法：
#   bash ~/.dc-platform/memory/patches/tgbot-dm-cursor-agent-restore/restore-dm-cursor-agent.sh
#   bash .../restore-dm-cursor-agent.sh --restart
#
# 背景：2026-11-21 曾把 TG_DM_EXEC_MODE 改成 wake_ide，私聊只交执行面、
# 结果不流式回 Telegram。定案改回 cursor_agent。本补丁在个人仓 youchu-memory。
set -euo pipefail

ROOT="${CHCODE_ROOT:-$HOME/Desktop/CHcode}"
BOT_DIR="$ROOT/omdb/tgbot"
ENVF="$BOT_DIR/.env"
RESTART=0
[[ "${1:-}" == "--restart" ]] && RESTART=1

if [[ ! -f "$ENVF" ]]; then
  echo "MISS $ENVF" >&2
  exit 1
fi

if grep -q '^TG_DM_EXEC_MODE=' "$ENVF"; then
  sed -i '' 's/^TG_DM_EXEC_MODE=.*/TG_DM_EXEC_MODE=cursor_agent/' "$ENVF"
else
  printf '\n# 私聊默认 Bot CLI 流式回 TG（勿用 wake_ide）\nTG_DM_EXEC_MODE=cursor_agent\n' >>"$ENVF"
fi

# 若存在 wake 模块：默认改回 cursor_agent（与 .env 一致）
CFG="$BOT_DIR/config.py"
WAKE="$BOT_DIR/tg_dm_ide_wake.py"
if [[ -f "$CFG" ]] && grep -q 'TG_DM_EXEC_MODE' "$CFG"; then
  # 只改默认字符串，不整文件重写
  BOT_DIR="$BOT_DIR" python3 - <<'PY'
from pathlib import Path
import os
p = Path(os.environ["BOT_DIR"]) / "config.py"
t = p.read_text(encoding="utf-8")
t2 = t.replace(
    "os.getenv('TG_DM_EXEC_MODE', 'wake_ide')",
    "os.getenv('TG_DM_EXEC_MODE', 'cursor_agent')",
).replace(
    'os.getenv("TG_DM_EXEC_MODE", "wake_ide")',
    'os.getenv("TG_DM_EXEC_MODE", "cursor_agent")',
)
if t2 != t:
    p.write_text(t2, encoding="utf-8")
    print("config.py default -> cursor_agent")
else:
    print("config.py: no wake_ide default (ok)")
PY
fi

if [[ -f "$WAKE" ]]; then
  BOT_DIR="$BOT_DIR" python3 - <<'PY'
from pathlib import Path
import os
p = Path(os.environ["BOT_DIR"]) / "tg_dm_ide_wake.py"
t = p.read_text(encoding="utf-8")
t2 = t.replace(
    "os.getenv('TG_DM_EXEC_MODE', 'wake_ide')",
    "os.getenv('TG_DM_EXEC_MODE', 'cursor_agent')",
).replace(
    'os.getenv("TG_DM_EXEC_MODE", "wake_ide")',
    'os.getenv("TG_DM_EXEC_MODE", "cursor_agent")',
)
if t2 != t:
    p.write_text(t2, encoding="utf-8")
    print("tg_dm_ide_wake.py default -> cursor_agent")
else:
    print("tg_dm_ide_wake.py: already cursor_agent or no default")
PY
fi

echo "TG_DM_EXEC_MODE=$(grep '^TG_DM_EXEC_MODE=' "$ENVF")"

if [[ "$RESTART" -eq 1 ]]; then
  if [[ -x "$BOT_DIR/deploy_app_support_runtime.sh" ]]; then
    bash "$BOT_DIR/deploy_app_support_runtime.sh"
  elif [[ -x "$HOME/Library/Application Support/tgbot-dc/scripts/start.sh" ]]; then
    bash "$HOME/Library/Application Support/tgbot-dc/scripts/start.sh"
  else
    echo "WARN: no deploy/start script; .env 已改，请手动重启 tgbot" >&2
  fi
fi

echo "OK: private DM replies via cursor_agent (Bot CLI streams back to Telegram)"
