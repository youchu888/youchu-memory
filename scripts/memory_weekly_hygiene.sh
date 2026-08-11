#!/usr/bin/env bash
# 记忆周清理：备份 + 体积/重复线索报告（不自动删正文）
# 用法：
#   bash ~/.dc-platform/scripts/memory_weekly_hygiene.sh
#   bash ~/.dc-platform/scripts/memory_weekly_hygiene.sh --dry-run
set -euo pipefail

MEMORY_ROOT="${HOME}/.dc-platform/memory"
LESSONS_DIR="${MEMORY_ROOT}/lessons"
OPEN_FILE="${MEMORY_ROOT}/MEMORY_OPEN.md"
PINNED_FILE="${MEMORY_ROOT}/PINNED.md"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

stamp="$(date '+%Y-%m-%d_%H%M%S')"
month="$(date '+%Y-%m')"
BACKUP_ROOT="${MEMORY_ROOT}/archives/${month}/memory-hygiene-${stamp}"

echo "=== memory weekly hygiene ==="
echo "root: ${MEMORY_ROOT}"
echo "dry_run: ${DRY_RUN}"

if [[ "${DRY_RUN}" -eq 0 ]]; then
  mkdir -p "${BACKUP_ROOT}"
  for f in MEMORY.md MEMORY_OPEN.md PINNED.md lessons/_index.md; do
    [[ -f "${MEMORY_ROOT}/${f}" ]] || continue
    mkdir -p "${BACKUP_ROOT}/$(dirname "${f}")"
    cp -p "${MEMORY_ROOT}/${f}" "${BACKUP_ROOT}/${f}"
  done
  echo "backup: ${BACKUP_ROOT}"
else
  echo "backup: skipped (--dry-run)"
fi

echo ""
echo "## sizes"
for f in MEMORY_OPEN.md PINNED.md MEMORY.md; do
  p="${MEMORY_ROOT}/${f}"
  if [[ -f "${p}" ]]; then
    b=$(wc -c < "${p}" | tr -d ' ')
    flag=""
    if [[ "${f}" == "MEMORY_OPEN.md" && "${b}" -gt 3072 ]]; then
      flag=" ⚠️ >3KB"
    fi
    if [[ "${f}" == "PINNED.md" ]]; then
      n=$(grep -cE '^[0-9]+\.' "${p}" 2>/dev/null || echo 0)
      flag=" (entries=${n}; cap=30)"
      [[ "${n}" -gt 30 ]] && flag="${flag} ⚠️"
    fi
    echo "- ${f}: ${b}B${flag}"
  else
    echo "- ${f}: MISSING"
  fi
done

ws_boot="${WORKSPACE_ROOT:-${HOME}/Desktop/CHcode}/.cursor/.agent-memory-bootstrap.md"
if [[ -f "${ws_boot}" ]]; then
  echo "- bootstrap: $(wc -c < "${ws_boot}" | tr -d ' ')B  (${ws_boot})"
fi

echo ""
echo "## OPEN open checkboxes"
if [[ -f "${OPEN_FILE}" ]]; then
  grep -E '^- \[[ ]\]' "${OPEN_FILE}" || echo "(none)"
else
  echo "MISSING MEMORY_OPEN.md"
fi

echo ""
echo "## possible duplicate title stems (lessons vs feedback, heuristic)"
# 取 lesson 标题词与 feedback 文件名粗碰撞
python3 - <<'PY'
import re
from pathlib import Path
root = Path.home() / ".dc-platform" / "memory"
lessons = root / "lessons"
# stem tokens from recent lesson titles
tokens = {}
for f in lessons.glob("*.md"):
    if f.name.startswith("_"):
        continue
    if not f.is_file():
        continue
    try:
        body = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    title = ""
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip().lower()
            break
    if not title:
        continue
    for tok in re.findall(r"[\u4e00-\u9fff]{2,}|[a-z]{4,}", title):
        tokens.setdefault(tok, []).append(f.name)

hits = []
for fb in root.glob("feedback_*.md"):
    name = fb.stem.replace("feedback_", "").replace("_", " ").lower()
    for tok, files in tokens.items():
        if tok in name and len(tok) >= 2:
            hits.append((tok, fb.name, files[:3]))

# unique by feedback
seen = set()
count = 0
for tok, fb, files in sorted(hits, key=lambda x: x[0]):
    key = (fb, tok)
    if key in seen:
        continue
    seen.add(key)
    print(f"- token={tok!r} feedback={fb} lessons≈{files}")
    count += 1
    if count >= 15:
        print("...(cap 15)")
        break
if count == 0:
    print("(no obvious collisions; still manually review same-topic pairs)")
PY

echo ""
echo "## project_* without exit hint (heuristic)"
find "${MEMORY_ROOT}" -maxdepth 1 -name 'project_*.md' -print 2>/dev/null | sort | while read -r f; do
  if ! grep -qiE '退出|exit|done|已结|归档|status:\s*(done|closed)' "${f}" 2>/dev/null; then
    echo "- $(basename "${f}") — 未检出退出/已结字样，请人工确认"
  fi
done | head -20

echo ""
echo "## checklist"
echo "见: ${MEMORY_ROOT}/playbook_memory_hygiene.md"
echo "OK"
