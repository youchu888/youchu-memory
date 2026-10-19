#!/usr/bin/env bash
# 根据 MEMORY_OPEN / 最近动过 / 活跃 session 生成 Agent 启动记忆包（瘦身版）
# 规则不在启动时全文注入。做到某件事时用 lookup-rules.sh 按关键词查 PINNED 和 lessons。
# 输出：$WORKSPACE/.cursor/.agent-memory-bootstrap.md
set -euo pipefail

MEMORY_ROOT="${HOME}/.dc-platform/memory"
LESSONS_DIR="${MEMORY_ROOT}/lessons"
PROJECTS_INDEX="${HOME}/.dc-platform/projects/INDEX.md"
PINNED_FILE="${MEMORY_ROOT}/PINNED.md"
OPEN_FILE="${MEMORY_ROOT}/MEMORY_OPEN.md"

WORKSPACE="${1:-${WORKSPACE_ROOT:-}}"
if [[ -z "${WORKSPACE}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [[ -d "${SCRIPT_DIR}/../../.cursor" ]]; then
    WORKSPACE="$(cd "${SCRIPT_DIR}/../.." && pwd)"
  else
    WORKSPACE="$(pwd)"
  fi
fi

OUT_DIR="${WORKSPACE}/.cursor"
OUT_FILE="${OUT_DIR}/.agent-memory-bootstrap.md"
REGISTRY="${WORKSPACE}/.cursor/projects/registry.yaml"

mkdir -p "${OUT_DIR}"

NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"

# 一句话 hook：优先 index 行，否则取首个 # 标题
_hook_for() {
  local f="$1" base hook
  base="$(basename "${f}")"
  hook=$(grep -F "(${base})" "${MEMORY_ROOT}/MEMORY.md" 2>/dev/null | head -1 | sed 's/.*— //' || true)
  if [[ -z "${hook}" ]]; then
    hook=$(grep -m1 '^# ' "${f}" 2>/dev/null | sed 's/^# //' || echo "${base}")
  fi
  # 单行截断
  echo "${hook}" | tr '\n' ' ' | sed 's/  */ /g' | cut -c1-120
}

{
  echo "# 又初 · 会话记忆启动包"
  echo ""
  echo "> **生成时间**：${NOW}"
  echo "> **维护人**：又初 · **来源**：\`MEMORY_OPEN.md\` + recent-by-mtime"
  echo "> **指令**：先读本文件里的未结事项。做到某件事时再 \`lookup-rules.sh\` 查对应规则，不要在启动时通读红线和经验。"
  echo "> **体积策略**：启动包只留未结和最近动过；规则按任务查。"
  echo ""

  # ── 0. 检索捷径（短）──
  echo "## 0. 检索捷径"
  echo ""
  DIR_INDEX="${MEMORY_ROOT}/project_chcode_directory_index.md"
  if [[ -f "${DIR_INDEX}" ]]; then
    sed -n '/^## 7\. 检索捷径/,/^## 变更记录/p' "${DIR_INDEX}" 2>/dev/null \
      | sed '/^## 变更记录/d' | head -12 || true
    echo ""
    echo "📄 \`~/.dc-platform/memory/project_chcode_directory_index.md\`"
  else
    echo "_目录索引未生成_"
  fi
  echo ""

  # ── 0.5 未结案 agent-bus（保留，但表格已由脚本自控）──
  OPEN_PY="${WORKSPACE}/.claude/database/scripts/notify/agent_bus_open.py"
  if [[ -f "${OPEN_PY}" ]]; then
    export AGENT_BUS_STATE_DIR="${AGENT_BUS_STATE_DIR:-$HOME/Library/Application Support/youchu-agent-bus/state}"
    export DC_PLATFORM_JSON="${DC_PLATFORM_JSON:-${WORKSPACE}/.claude/database/dc-platform.json}"
    # 已处理且无回复的旧单不进启动包。未结最多 3 条。
    python3 "${OPEN_PY}" --markdown 2>/dev/null | awk '
      BEGIN { rows=0 }
      /processed无reply/ { next }
      /^\| bus \|/ { print; next }
      /^\|[-| ]+\|$/ { print; next }
      /^\|/ {
        if (rows < 3) { print; rows++ }
        else if (rows == 3) { print "| … | … | _更早的未结用 agent-bus-open.sh_ |"; rows++ }
        next
      }
      { print }
    ' || echo "_agent-bus 未结案扫描失败_"
    echo ""
  fi

  # ── A. 规则不在启动时注入，做到再查 ──
  echo "## A. 规则（启动不读全文）"
  echo ""
  echo "做到哪件事，再查对应规则。启动包不放红线和经验正文。"
  echo ""
  echo "\`\`\`bash"
  echo "bash ~/.dc-platform/scripts/lookup-rules.sh 关键词"
  echo "\`\`\`"
  echo ""
  echo "红线在 \`PINNED.md\` 和 \`pinned/*.md\`。经验在 \`lessons/_index.md\`。聊天需求和讨论在 \`group_chat/reference.md\`。同一条命令一起查，每次每类最多 8 条。"
  echo ""

  # ── B. 未结交接 MEMORY_OPEN（全文，目标 ≤3KB）──
  echo "## B. 未结交接（MEMORY_OPEN）"
  echo ""
  if [[ -f "${OPEN_FILE}" ]]; then
    open_bytes=$(wc -c < "${OPEN_FILE}" | tr -d ' ')
    if [[ "${open_bytes}" -gt 3072 ]]; then
      echo "> ⚠️ OPEN 当前 ${open_bytes}B > 3KB，请删已结项后再依赖全文注入。"
      echo ""
    fi
    # 已结段落不进启动包
    awk 'NR==1 && /^# /{next} /^## 已结/{skip=1; next} /^## /{skip=0} skip{next} {print}' "${OPEN_FILE}"
  else
    echo "_缺少 MEMORY_OPEN.md（请建未结便条）_"
  fi
  echo ""

  # ── C. 按时间最近动过 top-5（与 hot 二维）──
  echo "## C. 按时间最近动过（top-5 · mtime）"
  echo ""
  echo "| 时间 | 文件 | 一句话 |"
  echo "|------|------|--------|"
  # lessons + feedback_*.md + project_*.md 按 mtime
  {
    find "${LESSONS_DIR}" -maxdepth 1 -name '*.md' ! -name '_*.md' -print 2>/dev/null
    find "${MEMORY_ROOT}" -maxdepth 1 \( -name 'feedback_*.md' -o -name 'project_*.md' -o -name 'reference_*.md' \) -print 2>/dev/null
  } | while IFS= read -r f; do
      [[ -f "${f}" ]] || continue
      # macOS stat
      mt=$(stat -f '%m' "${f}" 2>/dev/null || stat -c '%Y' "${f}" 2>/dev/null || echo 0)
      echo "${mt}|${f}"
    done \
    | sort -t'|' -k1,1nr \
    | head -5 \
    | while IFS='|' read -r mt f; do
        when=$(date -r "${mt}" '+%m-%d %H:%M' 2>/dev/null || date -d "@${mt}" '+%m-%d %H:%M' 2>/dev/null || echo "?")
        base=$(basename "${f}")
        hook=$(_hook_for "${f}")
        echo "| ${when} | \`${base}\` | ${hook} |"
      done || true
  echo ""
  echo "_打开≠用了；真改做法后再强化热度。深读用 tags / MCP。_"
  echo ""

  # ── D. 高优先级与经验索引：启动不展开，按任务查 ──
  echo "## D. 规则入口"
  echo ""
  echo "高优先级经验和历史索引不在启动时展开。做事时用上一节的 \`lookup-rules.sh\`。"
  echo ""

  echo "## F. 会话记录"
  echo ""
  echo "做到哪个 session，再读那个目录的 \`memory.md\`。启动不展开。"
  echo ""

  # ── G. 深读入口（不灌全量 MEMORY 行）──
  echo "## G. 深读入口"
  echo ""
  echo "- 全量索引：\`~/.dc-platform/memory/MEMORY.md\`"
  echo "- 周清理：\`playbook_memory_hygiene.md\` · \`scripts/memory_weekly_hygiene.sh\`"
  echo "- 狂人实操 v2：\`lessons/2026-08-11-worker-ant-memory-v2-practice.md\`"
  echo "- MCP：\`memory.list\` / \`memory.read\` / \`memory.write\`"
  echo ""

  echo "---"
  echo "_由 \`~/.dc-platform/scripts/load-memory-context.sh\` 在 sessionStart 生成，勿手改。_"

} > "${OUT_FILE}"

# 体积提示到 stderr（不进文件）
bytes=$(wc -c < "${OUT_FILE}" | tr -d ' ')
echo "${OUT_FILE} (${bytes} bytes)" >&2
echo "${OUT_FILE}"
