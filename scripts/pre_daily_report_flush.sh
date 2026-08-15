#!/usr/bin/env bash
# 日报前置冲刺（双机都要装）：把「当天任务」落到 work-log/hosts 并推 youchu-memory。
# 主人 2026-08-15：周一至周五 21:20（赶 21:30）；周六 18:20（赶 18:30）。周日跳过。
set -euo pipefail

export TZ="${TZ:-Asia/Shanghai}"
DAY="${1:-$(date '+%Y-%m-%d')}"
DOW="$(date '+%u')"
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
LOCAL_WL="${CHCODE_WORKLOG:-$HOME/Desktop/CHcode/.cursor/work-log}"
LOG_DIR="${HOME}/.dc-platform/logs"
LOG="$LOG_DIR/pre-daily-report-flush.log"
mkdir -p "$LOG_DIR" "$LOCAL_WL"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG"; }

if [[ "$DOW" == "7" ]]; then
  log "skip Sunday $DAY"
  exit 0
fi

if [[ -f "$MEM/.env.host" ]]; then
  # shellcheck disable=SC1091
  source "$MEM/.env.host"
fi
HOST_ID="${WORKLOG_HOST_ID:-unknown}"
log "flush start day=$DAY host=$HOST_ID"

# 1) 本机若还没有当日 work-log：从 ops-mirror 兜底写一份，避免 hosts 空白
DAY_FILE="$LOCAL_WL/$DAY.md"
OPS="$MEM/ops-mirror/hosts/${HOST_ID}/$DAY.md"
if [[ ! -s "$DAY_FILE" ]]; then
  mkdir -p "$LOCAL_WL"
  {
    echo "# work-log · $DAY"
    echo "> 自动冲刺生成 $(date '+%Y-%m-%d %H:%M:%S %z') · host=$HOST_ID"
    echo ""
    echo "## 已完成 / 进展"
    echo ""
    if [[ -s "$OPS" ]]; then
      echo "（来源 ops-mirror，收尾未手写时的兜底）"
      echo ""
      cat "$OPS"
    else
      echo "- （本机暂无手写流水；ops-mirror 也空。请次日补写或确认当日无实活）"
    fi
    echo ""
  } >"$DAY_FILE"
  log "seeded local work-log $DAY_FILE"
else
  log "local work-log already present $DAY_FILE"
fi

# 2) 导出 hosts + 推记忆仓（双机互相可见）
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
if [[ -f "$MEM/scripts/worklog_dual_mac_sync.py" ]]; then
  python3 "$MEM/scripts/worklog_dual_mac_sync.py" --date "$DAY" >>"$LOG" 2>&1 || log "warn: worklog export failed"
fi

bash "$HOME/.dc-platform/scripts/sync-memory-git.sh" \
  "chore: pre-daily-report flush $DAY $(date '+%H:%M') @$HOST_ID" >>"$LOG" 2>&1 \
  || log "warn: sync-memory-git failed"

HOST_OUT="$MEM/work-log/hosts/${HOST_ID}/$DAY.md"
if [[ -f "$HOST_OUT" ]]; then
  log "OK flushed hosts/$HOST_ID/$DAY.md → memory git"
else
  log "WARN still missing hosts/$HOST_ID/$DAY.md after flush"
  exit 1
fi
exit 0
