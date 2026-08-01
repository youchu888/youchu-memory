#!/usr/bin/env bash
# 日报前置：双机 memory 先同步，再打印 hosts 核对（主人 2026-08-01 铁律）
# 用法：bash ~/.dc-platform/scripts/prepare_daily_report_sync.sh [YYYY-MM-DD]
set -euo pipefail

DAY="${1:-$(TZ=Asia/Shanghai date '+%Y-%m-%d')}"
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
WL="$MEM/work-log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"

echo "=== 日报前置同步 · dt=$DAY ==="
bash "$HOME/.dc-platform/scripts/sync-memory-git.sh" \
  "chore: pre-daily-report sync $(date '+%Y-%m-%d %H:%M') @$(hostname -s)"

echo ""
echo "=== 双机 hosts 核对 · $DAY ==="
missing=0
for host in new-mac old-mac; do
  f="$WL/hosts/$host/$DAY.md"
  if [[ -f "$f" ]]; then
    lines=$(grep -E '^- ' "$f" | wc -l | tr -d ' ')
    echo "OK  $host  $f  (bullet≈$lines)"
  else
    echo "MISS $host  (无 $DAY.md)"
    missing=1
  fi
done

merged="$WL/$DAY.md"
if [[ -f "$merged" ]]; then
  echo "OK  merged  $merged"
else
  echo "MISS merged  $merged"
  missing=1
fi

echo ""
if [[ "$missing" -eq 1 ]]; then
  echo "WARN: 有主机缺流水。常见原因："
  echo "  1) 新 Mac 当天未写 CHcode/.cursor/work-log/$DAY.md"
  echo "  2) 新 Mac launchd com.youchu.memory-git-sync 未跑 / 机器休眠"
  echo "  3) Cursor transcript 不跨机；没写 work-log 则旧机永远汇不到"
  echo "继续汇总时：缺机须在日报回复里点明；禁止假装已双机齐全。"
else
  echo "OK: new-mac + old-mac 均有当日 hosts，可汇总日报。"
fi

echo ""
echo "next_read: $merged"
echo "hosts_dir: $WL/hosts/"
