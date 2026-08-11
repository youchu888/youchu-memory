#!/usr/bin/env bash
# 根据 PINNED / MEMORY_OPEN / lessons / 活跃 session 生成 Agent 启动记忆包（瘦身版）
# 对齐狂人记忆 v2：硬注入 pinned + hot + 按时间最近动过 + 未结便条；全量索引不灌进启动包
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
  echo "> **维护人**：又初 · **来源**：\`PINNED.md\` + \`MEMORY_OPEN.md\` + recent-by-mtime + high 标题"
  echo "> **指令**：先读本文件 → 再按任务 tags \`memory.read\` / 读完整 lesson。全量索引见 \`MEMORY.md\`（不整包注入）。"
  echo "> **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。"
  echo ""

  # ── 0. 检索捷径（短）──
  echo "## 0. 检索捷径"
  echo ""
  DIR_INDEX="${MEMORY_ROOT}/project_chcode_directory_index.md"
  if [[ -f "${DIR_INDEX}" ]]; then
    sed -n '/^## 7\. 检索捷径/,/^## 变更记录/p' "${DIR_INDEX}" 2>/dev/null \
      | sed '/^## 变更记录/d' | head -12
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
    # 限制体积：保留标题说明 + 最多 8 条未结（旧积压不占满冷启动）
    python3 "${OPEN_PY}" --markdown 2>/dev/null | awk '
      BEGIN { rows=0 }
      /^\| bus \|/ { print; next }
      /^\|[-| ]+\|$/ { print; next }
      /^\|/ {
        if (rows < 8) { print; rows++ }
        else if (rows == 8) { print "| … | … | _更多未结见 agent-bus-open.sh；此处已截断_ |"; rows++ }
        next
      }
      { print }
    ' || echo "_agent-bus 未结案扫描失败_"
    echo ""
  fi

  # ── A. PINNED 红线（全量硬注入）──
  echo "## A. 红线 pinned（必读）"
  echo ""
  if [[ -f "${PINNED_FILE}" ]]; then
    # 跳过标题/引用说明，保留编号条目
    awk '
      /^# / { next }
      /^>/ { next }
      /^$/ { next }
      /^[0-9]+\./ { print; c++; if (c>=30) exit }
    ' "${PINNED_FILE}"
  else
    echo "_缺少 PINNED.md_"
  fi
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
    # 去掉一级标题避免重复
    awk 'NR==1 && /^# /{next} {print}' "${OPEN_FILE}"
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
      done
  echo ""
  echo "_打开≠用了；真改做法后再强化热度。深读用 tags / MCP。_"
  echo ""

  # ── D. hot / high：仅标题+一行，上限 12（不再灌「正确做法」全文）──
  echo "## D. 高优先级标题（severity: high · 最多 12 条摘要）"
  echo ""
  high_count=0
  if [[ -d "${LESSONS_DIR}" ]]; then
    while IFS= read -r f; do
      [[ -f "${f}" ]] || continue
      if grep -q 'severity: high' "${f}" 2>/dev/null; then
        title=$(grep -m1 '^# ' "${f}" 2>/dev/null | sed 's/^# //' || basename "${f}")
        hook=$(_hook_for "${f}")
        echo "- **${title}** — ${hook}"
        echo "  📄 \`${f#${HOME}/}\`"
        high_count=$((high_count + 1))
        [[ "${high_count}" -ge 12 ]] && break
      fi
    done < <(find "${LESSONS_DIR}" -maxdepth 1 -name '*.md' ! -name '_*.md' -print 2>/dev/null | sort -r)
  fi
  [[ "${high_count}" -eq 0 ]] && echo "_（暂无 severity: high 的 lesson）_"
  echo ""

  # ── E. lessons 索引速览（只取最近表头 15 行）──
  echo "## E. lessons 索引速览（最近 15 行）"
  echo ""
  if [[ -f "${LESSONS_DIR}/_index.md" ]]; then
    echo "| 日期 | 标题 | tags | 一句话 |"
    echo "|------|------|------|--------|"
    awk 'NR>3 && /^\|/' "${LESSONS_DIR}/_index.md" 2>/dev/null | head -15 || true
    echo ""
    echo "📄 完整：\`~/.dc-platform/memory/lessons/_index.md\`"
  else
    echo "_lessons/_index.md 不存在_"
  fi
  echo ""

  # ── F. 活跃 Dev Session（摘要）──
  echo "## F. 活跃 Dev Session"
  echo ""
  session_count=0
  if [[ -f "${REGISTRY}" ]]; then
    while IFS= read -r rel; do
      [[ -n "${rel}" ]] || continue
      mem="${WORKSPACE}/${rel}/memory.md"
      if [[ -f "${mem}" ]]; then
        echo "### ${rel}"
        grep -E '^## |^- [0-9]{4}-' "${mem}" 2>/dev/null | head -8 || head -8 "${mem}"
        echo ""
        session_count=$((session_count + 1))
        [[ "${session_count}" -ge 5 ]] && break
      fi
    done < <(grep 'path:' "${REGISTRY}" 2>/dev/null | sed 's/.*path: *//' | tr -d ' "')
  fi
  [[ "${session_count}" -eq 0 ]] && echo "_无活跃 session memory.md_"
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
