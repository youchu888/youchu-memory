#!/usr/bin/env bash
# 用 git 同步 ~/.dc-platform/memory（不依赖局域网 IP，可两台互相协调）
set -euo pipefail

MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
BRANCH="${MEMORY_GIT_BRANCH:-main}"
MSG="${1:-chore: sync memory $(date '+%Y-%m-%d %H:%M') @$(hostname -s)}"

# launchd 下 PATH/ssh 环境极简：显式补全
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
SSH_KEY="${MEMORY_GIT_SSH_KEY:-$HOME/.ssh/id_ed25519}"
if [[ -f "$SSH_KEY" ]]; then
  export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
fi

cd "$MEM"

if [[ ! -d .git ]]; then
  echo "尚未 git init：$MEM"
  echo "见：~/.dc-platform/scripts/docs/memory_git_sync.md"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "未配置 origin。先建仓再："
  echo "  cd $MEM && git remote add origin <URL> && git push -u origin $BRANCH"
  exit 1
fi

# 防并发（定时任务与手动同时跑）
LOCK="$MEM/.git/.memory-sync.lock"
if command -v shlock >/dev/null 2>&1; then :; fi
exec 9>"$LOCK"
if ! flock -n 9 2>/dev/null; then
  # macOS 无 flock 时退化为 mkdir 锁
  if ! mkdir "$MEM/.git/.memory-sync.lockd" 2>/dev/null; then
    echo "另一同步进行中，跳过"
    exit 0
  fi
  trap 'rmdir "$MEM/.git/.memory-sync.lockd" 2>/dev/null || true' EXIT
fi

git add -A
if git diff --cached --quiet && git diff --quiet; then
  echo "本地无新改动"
else
  git commit -m "$MSG" || true
fi

# 先拉再推：两台互相协调，较新提交合并
if ! git pull --rebase --autostash origin "$BRANCH"; then
  echo "pull --rebase 冲突：手动解决后 git add -A && git rebase --continue && git push"
  git rebase --abort 2>/dev/null || true
  exit 2
fi
git push origin "$BRANCH"
echo "✓ memory 已同步 → $(git remote get-url origin) ($BRANCH) @$(date '+%H:%M:%S')"
