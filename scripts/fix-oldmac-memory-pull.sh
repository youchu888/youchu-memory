#!/usr/bin/env bash
# 旧 Mac：修复 memory pull 被未跟踪 AUTHORITY_HOST / 残留锁挡住
set -euo pipefail
MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
cd "$MEM"

# 保留本机身份
[[ -f .env.host ]] || echo 'export WORKLOG_HOST_ID=old-mac' > .env.host

# 清残留锁
rmdir .git/.memory-sync.lockd 2>/dev/null || true
rm -f .git/.memory-sync.lock 2>/dev/null || true

# 未跟踪且远端已有 → 移走（内容与远端 AUTHORITY_HOST 相同即可丢）
mkdir -p .git/untracked-backup
if [[ -f work-log/AUTHORITY_HOST ]] && ! git ls-files --error-unmatch work-log/AUTHORITY_HOST >/dev/null 2>&1; then
  mv work-log/AUTHORITY_HOST ".git/untracked-backup/AUTHORITY_HOST-$(date +%s)"
  echo "已移走未跟踪 work-log/AUTHORITY_HOST"
fi

git fetch origin
# 无本地独有提交时，直接对齐远端（最稳）
if [[ -z "$(git log --oneline origin/main..HEAD 2>/dev/null)" ]]; then
  git reset --hard origin/main
else
  git pull --rebase --autostash origin main
fi

# 再跑正式同步（会导出 old-mac 流水并推送）
# shellcheck disable=SC1091
source .env.host
bash "$HOME/.dc-platform/scripts/sync-memory-git.sh" "chore: old-mac recover sync $(date '+%Y-%m-%d %H:%M')"
echo "✓ 旧机 memory 已对齐并同步"
