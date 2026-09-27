#!/usr/bin/env bash
# 定时拉取 CHcode（dc-parent）业务仓，默认分支 dev。
# 不提交、不 push、不 force；有本地改动用 autostash；冲突则记日志退出。
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin:${PATH}"
export GIT_TERMINAL_PROMPT=0
export TZ="${TZ:-Asia/Shanghai}"

REPO="${CHCODE_ROOT:-$HOME/Desktop/CHcode}"
LOG_DIR="${CHCODE_GIT_LOG_DIR:-$HOME/.dc-platform/logs}"
LOG="${LOG_DIR}/chcode-git-sync.log"
mkdir -p "$LOG_DIR"

ts() { date '+%F %T'; }

{
  echo "[$(ts)] === chcode-git-sync start repo=$REPO ==="
  if [[ ! -d "$REPO/.git" ]]; then
    echo "[$(ts)] ERROR: 不是 git 仓: $REPO"
    exit 1
  fi

  cd "$REPO"
  BRANCH="${CHCODE_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
  if [[ "$BRANCH" == "HEAD" ]]; then
    BRANCH="${CHCODE_BRANCH:-dev}"
  fi

  # 脏工作区只提示，仍尝试 autostash pull
  if ! git diff --quiet || ! git diff --cached --quiet || [[ -n "$(git status --porcelain 2>/dev/null | head -1)" ]]; then
    echo "[$(ts)] WARN: 工作区有本地改动，将用 pull --rebase --autostash"
  fi

  BEFORE="$(git rev-parse --short HEAD 2>/dev/null || echo '?')"
  git fetch origin "$BRANCH"
  if git pull --rebase --autostash origin "$BRANCH"; then
    AFTER="$(git rev-parse --short HEAD)"
    # autostash 回存失败时仍可能 exit 0，需检查未合并路径
    if git status --porcelain 2>/dev/null | awk '{print $1}' | rg -q '^(UU|AA|DD|AU|UA|DU|UD)$'; then
      echo "[$(ts)] ERROR: pull 后仍有未合并文件（多为 autostash 冲突）。请本机打开仓库处理。"
      git status --porcelain | head -30 || true
      exit 1
    fi
    if [[ "$BEFORE" == "$AFTER" ]]; then
      echo "[$(ts)] OK 已是最新 branch=$BRANCH @$AFTER"
    else
      echo "[$(ts)] OK 已更新 $BEFORE → $AFTER branch=$BRANCH"
      git log --oneline "${BEFORE}..${AFTER}" 2>/dev/null | head -20 || true
    fi
  else
    echo "[$(ts)] ERROR: pull 失败（可能冲突）。请本机手动处理，勿 force。"
    git rebase --abort 2>/dev/null || true
    exit 1
  fi
  echo "[$(ts)] === done ==="
} >>"$LOG" 2>&1
