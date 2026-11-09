#!/usr/bin/env bash
# TG 群聊日学习之后：把有用内容融进已有记忆，不叠废话。
# 调用方：daily_group_chat_learn.py 学完自动跑；也可手动：
#   bash ~/.dc-platform/scripts/memory-fuse-after-tg-learn.sh --day YYYY-MM-DD
set -euo pipefail

TZ=Asia/Shanghai
export TZ

MEMORY="${HOME}/.dc-platform/memory"
WORKSPACE="${WORKSPACE_ROOT:-${HOME}/Desktop/CHcode}"
LOG_DIR="${HOME}/.dc-platform/logs"
LOG="${LOG_DIR}/memory-fuse-after-tg-learn.log"
LOAD_SH="${HOME}/.dc-platform/scripts/load-memory-context.sh"
REF="${MEMORY}/group_chat/reference.md"
REF_ARCHIVE_DIR="${MEMORY}/group_chat/archive"
OPEN_REQ="${MEMORY}/group_chat/open_requirements.md"
SETTLED="${MEMORY}/group_chat/metrics_settled.md"

DAY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --day) DAY="${2:-}"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
DAY="${DAY:-$(date '+%Y-%m-%d')}"

mkdir -p "$LOG_DIR" "$REF_ARCHIVE_DIR"

{
  echo "[$(date '+%F %T')] fuse-after-tg-learn start day=$DAY"

  # 1) 聊天参考：精确去重 + 近重复（去日期后正文相同）只留一行
  if [[ -f "$REF" ]]; then
    python3 - "$REF" "$REF_ARCHIVE_DIR" "$DAY" <<'PY'
import re, sys
from datetime import datetime, timedelta
from pathlib import Path

ref_path = Path(sys.argv[1])
arch_dir = Path(sys.argv[2])
day = sys.argv[3]
text = ref_path.read_text(encoding="utf-8")
lines = text.splitlines()
header, body = [], []
for i, line in enumerate(lines):
    if line.startswith("- "):
        body = lines[i:]
        header = lines[:i]
        break
    header.append(line)
else:
    print("reference: no bullets")
    raise SystemExit(0)

def norm(s: str) -> str:
    s = re.sub(r"^-?\s*\d{4}-\d{2}-\d{2}\s*", "", s.strip())
    return re.sub(r"\s+", "", s)

keep, seen, rolled = [], set(), []
cutoff = (datetime.strptime(day, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
for line in body:
    if not line.startswith("- "):
        continue
    m = re.match(r"^- (\d{4}-\d{2}-\d{2})\b", line)
    if m and m.group(1) < cutoff:
        rolled.append(line)
        continue
    key = norm(line)
    if not key or key in seen:
        continue
    # 短近重复：核心片段已出现则跳过
    core = key[12:] if len(key) > 36 else key
    if core and any(core in s or s in core for s in seen if len(s) >= 24):
        continue
    seen.add(key)
    keep.append(line)

arch_dir.mkdir(parents=True, exist_ok=True)
if rolled:
    month = cutoff[:7]
    arch = arch_dir / f"reference_rollover_{month}.md"
    prefix = "" if arch.exists() and arch.stat().st_size else f"# 聊天参考滚动归档 · {month}\n\n"
    with arch.open("a", encoding="utf-8") as f:
        f.write(prefix)
        f.write(f"## rollover from fuse {day}\n")
        f.write("\n".join(rolled) + "\n")
    print(f"reference: rolled {len(rolled)} old lines -> {arch}")

out = "\n".join(header).rstrip() + "\n\n" + "\n".join(keep) + "\n"
ref_path.write_text(out, encoding="utf-8")
print(f"reference: kept {len(keep)} (was {len(body)})")
PY
  else
    echo "reference: missing"
  fi

  # 2) 未做需求 / 已统一指标：精确去重
  for f in "$OPEN_REQ" "$SETTLED"; do
    [[ -f "$f" ]] || continue
    python3 - "$f" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").splitlines()
out, seen = [], set()
for line in lines:
    if line.startswith("- "):
        if line in seen:
            continue
        seen.add(line)
    out.append(line)
p.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
print(f"{p.name}: unique bullets={sum(1 for x in out if x.startswith('- '))}")
PY
  done

  # 3) 重生 bootstrap（次日冷启动瘦包）
  if [[ -f "$LOAD_SH" ]]; then
    bash "$LOAD_SH" "$WORKSPACE" >/dev/null || true
    boot="${WORKSPACE}/.cursor/.agent-memory-bootstrap.md"
    if [[ -f "$boot" ]]; then
      echo "bootstrap=$(wc -c <"$boot" | tr -d ' ')B"
    fi
  fi

  # 4) OPEN 体积提醒（只报不删）
  if [[ -f "$MEMORY/MEMORY_OPEN.md" ]]; then
    ob=$(wc -c <"$MEMORY/MEMORY_OPEN.md" | tr -d ' ')
    echo "OPEN=${ob}B cap=3072"
    [[ "$ob" -gt 3072 ]] && echo "WARN OPEN>3KB: 删已结项，勿继续叠"
  fi

  # 5) 落盘融合摘要
  report_dir="${MEMORY}/archives/$(date '+%Y-%m')/tg-learn-fuse"
  mkdir -p "$report_dir"
  {
    echo "# TG 学习后记忆融合 · ${DAY}"
    echo ""
    echo "- 原则: 废话不入；有用内容并入已有 feedback/lesson/settled；少新建"
    echo "- reference / open_requirements / metrics_settled 已去重"
    echo "- bootstrap 已重生"
  } >"${report_dir}/${DAY}.md"
  echo "wrote ${report_dir}/${DAY}.md"

  echo "[$(date '+%F %T')] fuse-after-tg-learn done"
} | tee -a "$LOG"
