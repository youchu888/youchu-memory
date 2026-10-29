#!/usr/bin/env bash
# 旧机：模拟 bot 调 cursor-agent（json+workspace+长prompt），定位空输出
set -euo pipefail
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
AGENT="$(command -v cursor-agent || command -v agent)"
WS="${TGBOT_PROJECT_ROOT:-$HOME/Desktop/CHcode}"
KEY="$(python3 - <<PY
import re
from pathlib import Path
t=Path("$TGBOT_DIR/.env").read_text()
m=re.search(r'^CURSOR_API_KEY=(.+)$',t,re.M)
print(m.group(1).strip().strip('"').strip("'") if m else '')
PY
)"
[[ -n "$KEY" ]] || { echo "no CURSOR_API_KEY"; exit 1; }
PROMPT_FILE="$(mktemp /tmp/tgbot_diag_prompt.XXXXXX.md)"
python3 - <<PY
from pathlib import Path
boot = Path.home() / "Desktop/CHcode/.cursor/.agent-memory-bootstrap.md"
body = boot.read_text(encoding="utf-8", errors="replace")[:12000] if boot.is_file() else "no bootstrap"
Path("$PROMPT_FILE").write_text(
    "# diag\n\n" + body + "\n\n---\n\n当前问题：只回复一个词 pong\n",
    encoding="utf-8",
)
print("prompt_chars", Path("$PROMPT_FILE").stat().st_size)
PY
echo "agent=$AGENT ws=$WS"
set +e
"$AGENT" --print --output-format json --trust --sandbox disabled --force \
  --api-key "$KEY" --workspace "$WS" --model auto \
  -p "请先完整阅读并严格执行文件：$PROMPT_FILE 然后直接回答末尾当前问题。不要只复述。" \
  > /tmp/tgbot_diag_out.json 2> /tmp/tgbot_diag_err.txt
RC=$?
set -e
echo "rc=$RC out_bytes=$(wc -c </tmp/tgbot_diag_out.json) err_bytes=$(wc -c </tmp/tgbot_diag_err.txt)"
echo "--- stdout head ---"; head -c 400 /tmp/tgbot_diag_out.json; echo
echo "--- stderr head ---"; head -c 400 /tmp/tgbot_diag_err.txt; echo
rm -f "$PROMPT_FILE"
