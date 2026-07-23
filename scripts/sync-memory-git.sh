#!/usr/bin/env bash
# 用 git 全自动同步 ~/.dc-platform/memory（双 Mac，不依赖局域网）
# - launchd 每 10 分钟
# - work-log 双机合并
# - rebase 冲突尽量自愈（work-log 时间戳类）；失败则安全回退到 origin 再推本机 hosts
set -euo pipefail

MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
BRANCH="${MEMORY_GIT_BRANCH:-main}"
MSG="${1:-chore: sync memory $(date '+%Y-%m-%d %H:%M') @$(hostname -s)}"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
SSH_KEY="${MEMORY_GIT_SSH_KEY:-$HOME/.ssh/id_ed25519}"
if [[ -f "$SSH_KEY" ]]; then
  export GIT_SSH_COMMAND="ssh -i $SSH_KEY -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
fi

# 仓内脚本更新后，自动覆盖 launchd 用的标准副本（双机全自动升级）
CANON="$MEM/scripts/sync-memory-git.sh"
SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
if [[ -f "$CANON" && "$CANON" -nt "$SELF" ]]; then
  cp -f "$CANON" "$SELF"
  chmod +x "$SELF"
  exec bash "$SELF" "$@"
fi

cd "$MEM"

if [[ ! -d .git ]]; then
  echo "尚未 git init：$MEM"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "未配置 origin"
  exit 1
fi

if [[ -f "$MEM/.env.host" ]]; then
  # shellcheck disable=SC1091
  source "$MEM/.env.host"
fi

# 清掉上次失败残留的 rebase/merge
if [[ -d .git/rebase-merge || -d .git/rebase-apply ]]; then
  echo "warn: 清除残留 rebase"
  git rebase --abort 2>/dev/null || true
fi
if [[ -f .git/MERGE_HEAD ]]; then
  echo "warn: 清除残留 merge"
  git merge --abort 2>/dev/null || true
fi

LOCK="$MEM/.git/.memory-sync.lock"
LOCKD="$MEM/.git/.memory-sync.lockd"
if [[ -d "$LOCKD" ]]; then
  if ! pgrep -f "sync-memory-git.sh" >/dev/null 2>&1; then
    echo "warn: 清除残留同步锁 $LOCKD"
    rmdir "$LOCKD" 2>/dev/null || true
  fi
fi
exec 9>"$LOCK"
if ! flock -n 9 2>/dev/null; then
  if ! mkdir "$LOCKD" 2>/dev/null; then
    echo "另一同步进行中，跳过"
    exit 0
  fi
  trap 'rmdir "$LOCKD" 2>/dev/null || true' EXIT
fi

WL_SYNC="$MEM/scripts/worklog_dual_mac_sync.py"
_run_worklog() {
  if [[ -f "$WL_SYNC" ]]; then
    python3 "$WL_SYNC" || echo "warn: worklog_dual_mac_sync 失败（继续 memory sync）"
  fi
}

_run_worklog

git add -A
if git diff --cached --quiet && git diff --quiet; then
  echo "本地无新改动"
else
  git commit -m "$MSG" || true
fi

git fetch origin "$BRANCH"

# 移走会挡住 pull 的「未跟踪但远端已有」文件
BACKUP_DIR="$MEM/.git/untracked-backup"
mkdir -p "$BACKUP_DIR"
REMOTE_LIST="$BACKUP_DIR/remote-files.$$.list"
git ls-tree -r --name-only "origin/$BRANCH" >"$REMOTE_LIST"
while IFS= read -r f; do
  [[ -z "$f" || ! -e "$f" ]] && continue
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    continue
  fi
  if git cat-file -e "origin/$BRANCH:$f" 2>/dev/null; then
    dest="$BACKUP_DIR/$(echo "$f" | tr '/' '_')-$(date +%s)"
    echo "warn: move untracked conflict: $f -> $dest"
    mv "$f" "$dest"
  fi
done <"$REMOTE_LIST"
rm -f "$REMOTE_LIST"

# 尝试自愈 rebase 冲突（主要针对 work-log 合并稿）
_heal_rebase_conflicts() {
  local conflicted only_safe=1
  conflicted="$(git diff --name-only --diff-filter=U 2>/dev/null || true)"
  [[ -z "$conflicted" ]] && return 1
  echo "warn: rebase 冲突，尝试自愈："
  echo "$conflicted"
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    case "$f" in
      work-log/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md)
        # 日合并稿：先取远端，稍后用 worklog 脚本重算
        git checkout --theirs -- "$f" 2>/dev/null || git checkout --ours -- "$f"
        git add -- "$f"
        ;;
      work-log/hosts/*)
        # 各机 hosts 目录：尽量两边都留——冲突时保留 ours，对端下一轮会再推
        git checkout --ours -- "$f" 2>/dev/null || git checkout --theirs -- "$f"
        git add -- "$f"
        ;;
      recall_index.jsonl|tgbot_session_carry.md|recall_shortcuts.md)
        # 索引类：取较新策略——先 theirs，本机 distill 后会再写
        git checkout --theirs -- "$f" 2>/dev/null || git checkout --ours -- "$f"
        git add -- "$f"
        ;;
      *)
        only_safe=0
        echo "warn: 非白名单冲突，不敢自动解: $f"
        ;;
    esac
  done <<< "$conflicted"
  if [[ "$only_safe" != 1 ]]; then
    return 1
  fi
  if GIT_EDITOR=true git rebase --continue; then
    echo "OK: rebase 冲突已自愈"
    return 0
  fi
  return 1
}

_pull_rebase() {
  if git pull --rebase --autostash origin "$BRANCH"; then
    return 0
  fi
  echo "warn: pull --rebase 失败，进入自愈"
  if _heal_rebase_conflicts; then
    return 0
  fi
  # 自愈失败：中止 rebase，硬对齐远端，再导出本机流水重推（全自动兜底）
  echo "warn: 自愈失败 → reset 到 origin/$BRANCH 后重导本机 hosts"
  git rebase --abort 2>/dev/null || true
  git reset --hard "origin/$BRANCH"
  _run_worklog
  git add -A
  if ! git diff --cached --quiet; then
    git commit -m "chore: auto-heal resync $(date '+%Y-%m-%d %H:%M') @$(hostname -s)" || true
  fi
  return 0
}

_pull_rebase

# 拉完后再合并一次（吸收对端 hosts/）
_run_worklog
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  git commit -m "chore: merge dual-mac work-log $(date '+%Y-%m-%d %H:%M')" || true
fi

# push；若被抢先则再拉一次自愈后推
if ! git push origin "$BRANCH"; then
  echo "warn: push 被拒，再拉一次后重推"
  _pull_rebase
  _run_worklog
  git add -A
  if ! git diff --cached --quiet || ! git diff --quiet; then
    git commit -m "chore: sync after push-reject $(date '+%Y-%m-%d %H:%M')" || true
  fi
  git push origin "$BRANCH"
fi

echo "OK memory 已同步 -> $(git remote get-url origin) ($BRANCH) @$(date '+%H:%M:%S') [全自动]"
