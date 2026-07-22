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

# 可选：固定本机 host id（new-mac / old-mac），避免 hostname 撞名
if [[ -f "$MEM/.env.host" ]]; then
  # shellcheck disable=SC1091
  source "$MEM/.env.host"
fi

# 防并发（定时任务与手动同时跑）；清掉无进程的残留锁
LOCK="$MEM/.git/.memory-sync.lock"
LOCKD="$MEM/.git/.memory-sync.lockd"
if [[ -d "$LOCKD" ]]; then
  if ! pgrep -f "sync-memory-git.sh" >/dev/null 2>&1; then
    echo "warn: 清除残留同步锁 $LOCKD"
    rmdir "$LOCKD" 2>/dev/null || true
  fi
fi
if command -v shlock >/dev/null 2>&1; then :; fi
exec 9>"$LOCK"
if ! flock -n 9 2>/dev/null; then
  # macOS 无 flock 时退化为 mkdir 锁
  if ! mkdir "$LOCKD" 2>/dev/null; then
    echo "另一同步进行中，跳过"
    exit 0
  fi
  trap 'rmdir "$LOCKD" 2>/dev/null || true' EXIT
fi

# 双机 work-log：先导出本机流水到 hosts/<id>/，再进入 git 同步
WL_SYNC="$MEM/scripts/worklog_dual_mac_sync.py"
if [[ -f "$WL_SYNC" ]]; then
  python3 "$WL_SYNC" || echo "warn: worklog_dual_mac_sync 失败（继续 memory sync）"
fi

git add -A
if git diff --cached --quiet && git diff --quiet; then
  echo "本地无新改动"
else
  git commit -m "$MSG" || true
fi

# 先 fetch；移走会挡住 pull 的「未跟踪但远端已有」文件（常见：AUTHORITY_HOST）
git fetch origin "$BRANCH"
BACKUP_DIR="$MEM/.git/untracked-backup"
mkdir -p "$BACKUP_DIR"
while IFS= read -r f; do
  [[ -z "$f" || ! -e "$f" ]] && continue
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    continue
  fi
  # 远端已有同名路径 → 本地未跟踪会阻断 merge/ff
  if git cat-file -e "origin/$BRANCH:$f" 2>/dev/null; then
    dest="$BACKUP_DIR/$(echo "$f" | tr '/' '_')-$(date +%s)"
    echo "warn: 移走未跟踪冲突文件 $f → $dest"
    mv "$f" "$dest"
  fi
done < <(git ls-tree -r --name-only "origin/$BRANCH")

# 先拉再推：两台互相协调，较新提交合并
if ! git pull --rebase --autostash origin "$BRANCH"; then
  echo "pull --rebase 冲突：手动解决后 git add -A && git rebase --continue && git push"
  echo "若仅被未跟踪文件挡住，可：rm 冲突文件后 git reset --hard origin/$BRANCH"
  git rebase --abort 2>/dev/null || true
  exit 2
fi

# 拉完后再合并一次（吸收对端 hosts/）
if [[ -f "$WL_SYNC" ]]; then
  python3 "$WL_SYNC" || true
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "chore: merge dual-mac work-log $(date '+%Y-%m-%d %H:%M')" || true
  fi
fi

git push origin "$BRANCH"
echo "✓ memory 已同步 → $(git remote get-url origin) ($BRANCH) @$(date '+%H:%M:%S')"
