#!/usr/bin/env bash
# 修复「网页还有额度，TG 却一直报模型额度用尽」
# 适用：old-mac（跑 tgbot 的那台）
#
# 做啥：
# 1) 安装 patches/tgbot-model-quota-heal（收紧额度误判 + 鉴权/空输出不再冒充额度）
# 2) 清空 model_quota_state.json
# 3) 用 .env 里的 CURSOR_API_KEY 冒烟 cursor-agent（auto / composer-2.5-fast）
# 4) 可选重启 tgbot
#
# 用法：
#   bash ~/.dc-platform/memory/scripts/heal_tgbot_false_quota.sh
#   SKIP_RESTART=1 bash ~/.dc-platform/memory/scripts/heal_tgbot_false_quota.sh
set -euo pipefail

MEMORY_ROOT="${MEMORY_ROOT:-$HOME/.dc-platform/memory}"
PATCH_DIR="${PATCH_DIR:-$MEMORY_ROOT/patches/tgbot-model-quota-heal}"
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${TGBOT_DIR}/.bak_model_quota_heal_${STAMP}"
SKIP_RESTART="${SKIP_RESTART:-0}"

echo "=== heal tgbot false quota ==="
echo "host=$(hostname)  TGBOT_DIR=$TGBOT_DIR"

if [[ ! -d "$PATCH_DIR" ]]; then
  echo "[fail] patch dir missing: $PATCH_DIR" >&2
  echo "先跑 memory sync，确认 patches/tgbot-model-quota-heal 已到本机。" >&2
  exit 1
fi
if [[ ! -d "$TGBOT_DIR" ]]; then
  echo "[fail] tgbot dir missing: $TGBOT_DIR" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
FILES=(model_quota.py claude_client.py)
for f in "${FILES[@]}"; do
  [[ -f "$PATCH_DIR/$f" ]] || { echo "[fail] missing $PATCH_DIR/$f" >&2; exit 1; }
  [[ -f "$TGBOT_DIR/$f" ]] && cp "$TGBOT_DIR/$f" "$BACKUP_DIR/$f"
  cp "$PATCH_DIR/$f" "$TGBOT_DIR/$f"
  echo "[ok] installed $f (backup → $BACKUP_DIR/$f)"
done

rm -f "$TGBOT_DIR"/__pycache__/model_quota*.pyc \
  "$TGBOT_DIR"/__pycache__/claude_client*.pyc 2>/dev/null || true

STATE="$TGBOT_DIR/data/model_quota_state.json"
mkdir -p "$TGBOT_DIR/data"
printf '%s\n' '{
  "exhausted": {},
  "cleared_at": "'"${STAMP}"'",
  "note": "cleared by heal_tgbot_false_quota.sh"
}' > "$STATE"
echo "[ok] cleared $STATE"

# .env：fallback 链末尾补 auto（若还没有）
ENV_FILE="$TGBOT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  if grep -q '^CURSOR_MODEL_FALLBACK_CHAIN=' "$ENV_FILE"; then
    if ! grep -E '^CURSOR_MODEL_FALLBACK_CHAIN=.*\bauto\b' "$ENV_FILE" >/dev/null; then
      # 备份后追加 ,auto
      cp "$ENV_FILE" "$BACKUP_DIR/env.bak"
      python3 - <<'PY'
from pathlib import Path
import re
p = Path.home() / "Desktop/CHcode/omdb/tgbot/.env"
text = p.read_text(encoding="utf-8")
def repl(m):
    v = m.group(1).strip()
    if re.search(r'(^|,)\s*auto\s*(,|$)', v):
        return m.group(0)
    return f"CURSOR_MODEL_FALLBACK_CHAIN={v},auto"
text2, n = re.subn(r'^CURSOR_MODEL_FALLBACK_CHAIN=(.*)$', repl, text, count=1, flags=re.M)
if n:
    p.write_text(text2, encoding="utf-8")
    print("[ok] .env FALLBACK_CHAIN appended ,auto")
else:
    print("[warn] FALLBACK_CHAIN line not updated")
PY
    else
      echo "[ok] .env FALLBACK_CHAIN already has auto"
    fi
  else
    echo "[warn] .env 无 CURSOR_MODEL_FALLBACK_CHAIN，跳过"
  fi
fi

# 冒烟：cursor-agent + API key
export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"
AGENT_BIN="$(command -v cursor-agent || command -v agent || true)"
if [[ -z "$AGENT_BIN" ]]; then
  echo "[fail] cursor-agent/agent 不在 PATH" >&2
  exit 2
fi
echo "[info] agent=$AGENT_BIN"

PYTHON=python3
if [[ -x "$TGBOT_DIR/.venv/bin/python" ]]; then
  PYTHON="$TGBOT_DIR/.venv/bin/python"
elif [[ -x "$TGBOT_DIR/venv/bin/python" ]]; then
  PYTHON="$TGBOT_DIR/venv/bin/python"
fi
echo "[info] python=$PYTHON"
# conda base 常缺 dotenv；自检前尽量补上（失败不阻断，后面有 stub）
"$PYTHON" -c "import dotenv" 2>/dev/null || \
  "$PYTHON" -m pip install -q python-dotenv 2>/dev/null || true

"$PYTHON" - <<'PY'
import os, re, subprocess, sys
from pathlib import Path
env_path = Path.home() / "Desktop/CHcode/omdb/tgbot/.env"
text = env_path.read_text(encoding="utf-8") if env_path.is_file() else ""
m = re.search(r"^CURSOR_API_KEY=(.+)$", text, re.M)
key = (m.group(1).strip().strip('"').strip("'") if m else "")
if not key:
    print("[fail] .env 无 CURSOR_API_KEY", file=sys.stderr)
    sys.exit(3)
env = os.environ.copy()
env["CURSOR_API_KEY"] = key
env["PATH"] = str(Path.home() / ".local/bin") + ":" + env.get("PATH", "")
agent = None
for cand in ("cursor-agent", "agent"):
    from shutil import which
    agent = which(cand)
    if agent:
        break
if not agent:
    print("[fail] agent binary missing", file=sys.stderr)
    sys.exit(2)
ok = 0
for model in ("auto", "composer-2.5-fast"):
    p = subprocess.run(
        [agent, "--print", "--output-format", "text", "--model", model, "-p", "只回复：pong"],
        capture_output=True, text=True, env=env, timeout=120,
    )
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    print(f"[smoke] model={model} rc={p.returncode} out={out[:80]!r} err={err[:120]!r}")
    if p.returncode == 0 and out:
        ok += 1
if ok == 0:
    print("[fail] 冒烟全失败：多半是 CURSOR_API_KEY 失效/过期，或 agent 未登录。网页 Pro+ 用量≠这把 key 的账号。", file=sys.stderr)
    sys.exit(4)
print(f"[ok] smoke passed ({ok}/2)")
PY

# 语法自检（缺 dotenv 时 stub，避免 conda base 中断整段 heal）
if ! "$PYTHON" - <<PY
import sys, types
sys.path.insert(0, r"$TGBOT_DIR")
if "dotenv" not in sys.modules:
    try:
        import dotenv  # noqa: F401
    except ModuleNotFoundError:
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda *a, **k: None
        sys.modules["dotenv"] = dotenv
import model_quota
assert model_quota.is_quota_error("resource_exhausted")
assert not model_quota.is_quota_error("刚才因额度用尽切到 fast")
assert model_quota.is_auth_error("Authentication required. Run agent login")
print("[ok] model_quota self-check")
PY
then
  echo "[warn] model_quota self-check 失败（多半是解释器缺依赖）；冒烟已过，继续重启 bot"
fi

if [[ "$SKIP_RESTART" == "1" ]]; then
  echo "[skip] restart (SKIP_RESTART=1)"
else
  if [[ -x "$TGBOT_DIR/restart.sh" ]]; then
    echo "[info] restarting tgbot..."
    (cd "$TGBOT_DIR" && bash ./restart.sh) || echo "[warn] restart.sh 非零退出，请手工确认 bot 进程"
  else
    echo "[warn] 无 restart.sh，请手工重启 tgbot"
  fi
fi

echo "=== heal done ==="
echo "下一步：TG 私聊发一句「在吗」验证复杂任务是否恢复。"
