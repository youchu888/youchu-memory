#!/usr/bin/env bash
# memory-git pull 后：仅在 old-mac 安装 TG 日学习 + 学后记忆融合
# 不经 SSH；靠 stamp 幂等
set -euo pipefail

MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
CFG="$MEM/config/oneshot_tg_learn_fuse_oldmac.env"
STATE_DIR="${HOME}/.dc-platform/state"
STAMP="$STATE_DIR/oneshot_tg_learn_fuse_oldmac.stamp"
LOG="$STATE_DIR/oneshot_tg_learn_fuse_oldmac.log"
RUNTIME_SCRIPTS="${HOME}/.dc-platform/scripts"
CHCODE="${WORKSPACE_ROOT:-$HOME/Desktop/CHcode}"
TGBOT="${CHCODE}/omdb/tgbot"
LABEL="com.youchu.daily-group-learn"

mkdir -p "$STATE_DIR" "$RUNTIME_SCRIPTS"
exec >>"$LOG" 2>&1
echo "==== $(date '+%Y-%m-%d %H:%M:%S') host=$(hostname -s) ===="

_host_id() {
  if [[ -f "$MEM/.env.host" ]]; then
    # shellcheck disable=SC1091
    source "$MEM/.env.host"
  fi
  echo "${WORKLOG_HOST_ID:-$(hostname -s)}"
}

host="$(_host_id)"
ENABLED=0
TARGET_HOST=old-mac
FORCE=0
if [[ -f "$CFG" ]]; then
  # shellcheck disable=SC1090
  source "$CFG"
fi

if [[ "${ENABLED}" != "1" ]]; then
  echo "skip: ENABLED!=1"
  exit 0
fi
if [[ "$host" != "$TARGET_HOST" ]]; then
  echo "skip: host=$host target=$TARGET_HOST"
  exit 0
fi
if [[ -f "$STAMP" && "${FORCE}" != "1" ]]; then
  echo "skip: stamp exists $STAMP"
  exit 0
fi

echo "install on $host ..."

# 1) 融合脚本 → runtime
if [[ -f "$MEM/scripts/memory-fuse-after-tg-learn.sh" ]]; then
  cp -f "$MEM/scripts/memory-fuse-after-tg-learn.sh" "$RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh"
  chmod +x "$RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh"
  echo "ok fuse -> $RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh"
fi

# 2) learn 脚本 → tgbot（仓内 + host-sync 双源）
mkdir -p "$TGBOT/scripts"
if [[ -f "$MEM/scripts/host-sync/daily_group_chat_learn.py" ]]; then
  cp -f "$MEM/scripts/host-sync/daily_group_chat_learn.py" "$TGBOT/scripts/daily_group_chat_learn.py"
  echo "ok learn from host-sync"
elif [[ -f "$CHCODE/omdb/tgbot/scripts/daily_group_chat_learn.py" ]]; then
  echo "ok learn already in chcode"
else
  echo "fail: learn script missing"
  exit 1
fi

# 3) 装 02:00 launchd
INSTALL_SH="$TGBOT/scripts/install_daily_group_learn_launchd.sh"
if [[ -f "$MEM/scripts/host-sync/install_daily_group_learn_launchd.sh" ]]; then
  cp -f "$MEM/scripts/host-sync/install_daily_group_learn_launchd.sh" "$INSTALL_SH"
fi
if [[ ! -f "$INSTALL_SH" ]]; then
  echo "fail: missing $INSTALL_SH"
  exit 1
fi
bash "$INSTALL_SH"

# 4) 立刻跑一次融合（对已有 reference 去重）；完整回拉留给 02:00
if [[ -x "$RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh" || -f "$RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh" ]]; then
  bash "$RUNTIME_SCRIPTS/memory-fuse-after-tg-learn.sh" --day "$(TZ=Asia/Shanghai date '+%Y-%m-%d')" || true
fi

DOMAIN="gui/$(id -u)"
launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1 && echo "launchd ok $LABEL" || echo "warn: launchd print failed"

date '+%Y-%m-%d %H:%M:%S' >"$STAMP"
echo "OK installed tg learn+fuse on $host stamp=$STAMP"

# work-log 一行，对端可见
day="$(date '+%Y-%m-%d')"
wl="$MEM/work-log/hosts/${host}/${day}.md"
mkdir -p "$(dirname "$wl")"
touch "$wl"
if ! grep -q 'tg-learn-fuse oneshot' "$wl" 2>/dev/null; then
  echo "- $(date '+%H:%M') tg-learn-fuse oneshot: installed launchd ${LABEL} + fuse" >>"$wl"
fi
