#!/usr/bin/env bash
# 做到某件事时按关键词查红线和经验。不要在启动时通读。
# 用法：bash lookup-rules.sh 关键词 [更多关键词]
set -euo pipefail

MEMORY_ROOT="${HOME}/.dc-platform/memory"
PINNED_FILE="${MEMORY_ROOT}/PINNED.md"
PINNED_DIR="${MEMORY_ROOT}/pinned"
INDEX_FILE="${MEMORY_ROOT}/lessons/_index.md"
CHAT_REF="${MEMORY_ROOT}/group_chat/reference.md"

if [[ $# -lt 1 ]]; then
  echo "用法：bash ~/.dc-platform/scripts/lookup-rules.sh 关键词 [更多关键词]" >&2
  echo "示例：bash ~/.dc-platform/scripts/lookup-rules.sh 日报 私聊" >&2
  exit 1
fi

pattern="$(printf '%s|' "$@" | sed 's/|$//')"

echo "## 红线"
echo ""
pinned_files=()
[[ -f "${PINNED_FILE}" ]] && pinned_files+=("${PINNED_FILE}")
if [[ -d "${PINNED_DIR}" ]]; then
  while IFS= read -r extra; do
    pinned_files+=("${extra}")
  done < <(find "${PINNED_DIR}" -maxdepth 1 -name '*.md' ! -name 'README.md' | sort)
fi

if [[ ${#pinned_files[@]} -eq 0 ]]; then
  echo "_缺少红线原文_"
else
  matched="$(grep -h -E '^[0-9]+\.' "${pinned_files[@]}" | grep -i -E "${pattern}" | head -8 || true)"
  if [[ -n "${matched}" ]]; then
    echo "${matched}"
  else
    echo "_红线里没有对上的条目_"
  fi
fi
echo ""

echo "## 经验索引"
echo ""
if [[ -f "${INDEX_FILE}" ]]; then
  matched="$(grep -E '^\| 20' "${INDEX_FILE}" | grep -i -E "${pattern}" | head -8 || true)"
  if [[ -n "${matched}" ]]; then
    echo "| 日期 | 标题 | tags | 一句话 |"
    echo "|------|------|------|--------|"
    echo "${matched}"
    echo ""
    echo "_经验最多 8 条。太多就把关键词说具体。_"
  else
    echo "_经验索引里没有对上的条目_"
  fi
else
  echo "_缺少 lessons/_index.md_"
fi
echo ""

echo "## 聊天参考"
echo ""
if [[ -f "${CHAT_REF}" ]]; then
  matched="$(grep -E '^- ' "${CHAT_REF}" | grep -i -E "${pattern}" | head -8 || true)"
  if [[ -n "${matched}" ]]; then
    echo "${matched}"
  else
    echo "_聊天参考里没有对上的条目_"
  fi
else
  echo "_还没有聊天参考_"
fi
echo ""
echo "只用上面命中的几条。不要打开红线全文、经验索引或当日聊天稿。"
