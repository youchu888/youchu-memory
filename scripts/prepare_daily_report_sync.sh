#!/usr/bin/env bash
# 日报前置：memory 先同步，再按权威机核对 hosts
# 单机（old-mac 停）：只要求 AUTHORITY_HOST 当日流水
# 双机：MEMORY_SYNC MODE=interval 时同时核对 old-mac
# 用法：bash ~/.dc-platform/scripts/prepare_daily_report_sync.sh [YYYY-MM-DD]
set -euo pipefail

DAY="${1:-$(TZ=Asia/Shanghai date '+%Y-%m-%d')}"
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
WL="$MEM/work-log"
CFG="$MEM/config/memory_sync.env"
AUTH_FILE="$WL/AUTHORITY_HOST"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"

_authority() {
  if [[ -n "${WORKLOG_AUTHORITY_HOST:-}" ]]; then
    echo "$WORKLOG_AUTHORITY_HOST"
    return
  fi
  if [[ -f "$AUTH_FILE" ]]; then
    while IFS= read -r line; do
      line="${line%%#*}"
      line="$(echo "$line" | tr -d '[:space:]')"
      [[ -n "$line" ]] && { echo "$line"; return; }
    done <"$AUTH_FILE"
  fi
  echo "new-mac"
}

_sync_mode() {
  if [[ -f "$CFG" ]]; then
    local m
    m="$(grep -E '^[[:space:]]*MODE=' "$CFG" | tail -1 | cut -d= -f2- | tr -d '[:space:]' || true)"
    [[ -n "$m" ]] && { echo "$m"; return; }
  fi
  echo "daily"
}

AUTH="$(_authority)"
MODE="$(_sync_mode)"

echo "=== 日报前置同步 · dt=$DAY authority=$AUTH mode=$MODE ==="
bash "$HOME/.dc-platform/scripts/sync-memory-git.sh" \
  "chore: pre-daily-report sync $(date '+%Y-%m-%d %H:%M') @$(hostname -s)"

echo ""
echo "=== hosts 核对 · $DAY ==="
missing=0
hosts_to_check=("$AUTH")
if [[ "$MODE" == "interval" ]]; then
  for h in new-mac old-mac; do
    [[ "$h" == "$AUTH" ]] && continue
    hosts_to_check+=("$h")
  done
fi

for host in "${hosts_to_check[@]}"; do
  f="$WL/hosts/$host/$DAY.md"
  if [[ -f "$f" ]]; then
    lines=$(grep -cE '^- ' "$f" 2>/dev/null || true)
    echo "OK  $host  $f  (bullet≈${lines:-0})"
  else
    echo "MISS $host  (无 $DAY.md)"
    missing=1
  fi
done

# 单机时若残留 old-mac 目录缺文件，只提示不计入缺机
if [[ "$MODE" != "interval" ]]; then
  peer="old-mac"
  [[ "$AUTH" == "old-mac" ]] && peer="new-mac"
  pf="$WL/hosts/$peer/$DAY.md"
  if [[ ! -f "$pf" ]]; then
    echo "INFO $peer 无当日流水（单机 MODE=daily，不阻断）"
  fi
fi

merged="$WL/$DAY.md"
if [[ -f "$merged" ]]; then
  echo "OK  merged  $merged"
else
  echo "MISS merged  $merged"
  missing=1
fi

echo ""
if [[ "$missing" -eq 1 ]]; then
  echo "WARN: 权威机或缺合并稿。常见原因："
  echo "  1) 权威机当天未写 CHcode/.cursor/work-log/$DAY.md"
  echo "  2) launchd com.youchu.memory-git-sync 未跑 / 机器休眠"
  echo "  3) 双机 MODE=interval 时对端未 sync"
else
  if [[ "$MODE" == "interval" ]]; then
    echo "OK: 权威机 + 对端 hosts 齐全，可汇总日报。"
  else
    echo "OK: 权威机 ($AUTH) hosts 齐全（单机），可汇总日报。"
  fi
fi

echo ""
echo "next_read: $merged"
echo "hosts_dir: $WL/hosts/"
