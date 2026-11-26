#!/usr/bin/env bash
# 查看只读镜像里的未结案（new-mac 对照用）。不启 poller。
set -euo pipefail
DIR="${AGENT_BUS_READONLY_DIR:-$HOME/Library/Application Support/youchu-agent-bus/readonly-mirror}"
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
AUTH="$(grep -E '^[^#]' "$MEM/work-log/AUTHORITY_HOST" 2>/dev/null | head -1 | tr -d '[:space:]' || echo old-mac)"

echo "AUTHORITY_HOST=$AUTH"
echo "readonly_dir=$DIR"
if [[ ! -d "$DIR" ]]; then
  echo "尚无只读副本。等权威机 export + memory-git-sync 拉取后再看。"
  echo "手动：python3 \"$MEM/scripts/export_agent_bus_readonly_mirror.py\" materialize"
  exit 0
fi
if [[ -f "$DIR/MANIFEST.json" ]]; then
  echo "--- MANIFEST ---"
  cat "$DIR/MANIFEST.json"
  echo
fi
if [[ -f "$DIR/OPEN.md" ]]; then
  echo "--- OPEN.md (head) ---"
  head -n 40 "$DIR/OPEN.md"
else
  echo "缺 OPEN.md"
fi
echo
echo "完整未结案：open $DIR/OPEN.md"
echo "提醒：只读对照；ack/reply 只在权威机做。"
