#!/usr/bin/env bash
# memory-git pull 后：仅 old-mac 跑一次「私聊 cursor_agent + 拉回 TG bot」
# 不经 SSH；靠 stamp 幂等。new-mac 必须已停 bot（否则 409 抢 token）。
set -euo pipefail

MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
CFG="$MEM/config/oneshot_reclaim_tgbot_oldmac.env"
STATE_DIR="${HOME}/.dc-platform/state"
STAMP="$STATE_DIR/oneshot_reclaim_tgbot_oldmac.stamp"
LOG="$STATE_DIR/oneshot_reclaim_tgbot_oldmac.log"
PATCH="$MEM/patches/tgbot-dm-cursor-agent-restore"
RECLAIM="$PATCH/reclaim-bot-on-old-mac.sh"

mkdir -p "$STATE_DIR"
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

if [[ ! -x "$RECLAIM" && ! -f "$RECLAIM" ]]; then
  echo "fail: missing $RECLAIM"
  exit 1
fi
chmod +x "$PATCH"/*.sh 2>/dev/null || true

echo "reclaim on $host ..."
bash "$RECLAIM"

date '+%Y-%m-%d %H:%M:%S' >"$STAMP"
echo "OK reclaim stamp=$STAMP"

# 成功后关掉开关，避免以后 FORCE 误开时空转意图不清
if [[ -f "$CFG" ]]; then
  if grep -q '^ENABLED=' "$CFG"; then
    sed -i '' 's/^ENABLED=.*/ENABLED=0/' "$CFG"
  else
    echo 'ENABLED=0' >>"$CFG"
  fi
  echo "ok set ENABLED=0 in $CFG"
fi

day="$(date '+%Y-%m-%d')"
wl="$MEM/work-log/hosts/${host}/${day}.md"
mkdir -p "$(dirname "$wl")"
touch "$wl"
if ! grep -q 'reclaim-tgbot oneshot' "$wl" 2>/dev/null; then
  echo "- $(date '+%H:%M') reclaim-tgbot oneshot: cursor_agent + bot 已拉回（stamp 已写）" >>"$wl"
fi
