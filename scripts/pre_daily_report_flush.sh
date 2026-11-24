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

# 主人 2026-10-02：法定假 / 请假日不冲刺日报流水
SKIP_PY="${CHCODE_ROOT:-$HOME/Desktop/CHcode}/.cursor/scripts/_skip_non_workday.py"
if [[ -f "$SKIP_PY" ]]; then
  _skip_reason="$(python3 "$SKIP_PY" --date "$DAY" 2>/dev/null || true)"
  if [[ -n "${_skip_reason// }" ]]; then
    log "skip non-workday $DAY ($_skip_reason) — 不冲刺日报"
    exit 0
  fi
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

# 1b) 空壳检测：仅有 ops-mirror/占位、没有业务短句 → 打 WARN（不中断 flush）
# 业务词与 auto_draft_daily_report._PREFER_RE 对齐口径
BIZ_HITS="$(
  python3 - "$DAY_FILE" <<'PY' || true
import re, sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
prefer = re.compile(
    r"(渠道|归因|漏斗|报表|建表|ETL|核查|指标|表|分区|补数|发布|试跑|抽检|口径|汇总|"
    r"标签|设备|数仓|维表|对账|看板|留存|充值|广告|推广|页面访问|次留|终身价值)",
    re.I,
)
thin_markers = ("ops-mirror", "暂无手写流水", "自动冲刺生成")
bullets = [ln[2:].strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
biz = [b for b in bullets if prefer.search(b)]
only_thin = (not biz) and (any(m in text for m in thin_markers) or not bullets)
print(f"biz={len(biz)};thin={1 if only_thin else 0}")
PY
)"
log "work-log quality $BIZ_HITS file=$DAY_FILE"
if [[ "$BIZ_HITS" == *thin=1* ]]; then
  log "WARN local work-log looks empty-shell (ops-mirror/placeholder only). IDE 实活须先写入 .cursor/work-log 再冲刺，否则权威机日报会漏。"
  if ! grep -q '流水偏空警告' "$DAY_FILE" 2>/dev/null; then
    {
      echo ""
      echo "> ⚠️ 流水偏空警告：当日对话实活若未写入本文件，双机同步后权威机定稿仍会漏项。见 `.cursor/rules/daily-worklog-required.mdc`"
      echo ""
    } >>"$DAY_FILE"
  fi
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
