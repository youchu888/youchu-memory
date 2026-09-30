#!/usr/bin/env bash
# 开机 / 登录 / 休眠唤醒后：确保自动化监控 LaunchAgent 已加载并在跑
# 由 com.youchu.automation-ensure 每 2 分钟 + RunAtLoad 调用
set -euo pipefail

DOMAIN="gui/$(id -u)"
LOG_DIR="${HOME}/.dc-platform/logs"
LOG="${LOG_DIR}/automation-ensure.log"
mkdir -p "$LOG_DIR"

# new-mac 交回 old-mac：本机不保活、不重装
if [[ -f "$HOME/.dc-platform/config/DISABLE_LOCAL_AUTOMATION" ]]; then
  echo "[$(date '+%F %T')] SKIP ensure（DISABLE_LOCAL_AUTOMATION）" | tee -a "$LOG" >/dev/null
  exit 0
fi

ts() { date '+%F %T'; }
log() { echo "[$(ts)] $*" | tee -a "$LOG" >/dev/null; echo "[$(ts)] $*"; }

# 常驻（KeepAlive）：必须有 PID
KEEPALIVE_LABELS=(
  com.dc.tgbot-daemon
  com.youchu.agent-bus-poller
  com.youchu.onehr-checkin
  com.youchu.ethan-jobs-watch
)

# 定时任务：只要已 load 即可（不必此刻有 PID）
LOADED_LABELS=(
  com.youchu.vpn-sync
  com.youchu.memory-git-sync
  com.youchu.chcode-git-sync
  com.youchu.daily-report-wake
  com.youchu.daily-report-fallback
  com.youchu.worker-ant-daily-learn
  com.youchu.memory-daily-light-tidy
)

plist_path() {
  echo "$HOME/Library/LaunchAgents/${1}.plist"
}

is_loaded() {
  launchctl print "$DOMAIN/$1" >/dev/null 2>&1
}

has_pid() {
  # launchctl list: PID 列非 "-"
  local line pid
  line="$(launchctl list 2>/dev/null | awk -v l="$1" '$3==l {print $1}')"
  [[ -n "$line" && "$line" != "-" ]]
}

ensure_loaded() {
  local label="$1" plist
  plist="$(plist_path "$label")"
  if [[ ! -f "$plist" ]]; then
    log "SKIP $label（无 plist）"
    return 0
  fi
  if is_loaded "$label"; then
    return 0
  fi
  log "bootstrap $label"
  launchctl bootstrap "$DOMAIN" "$plist" 2>>"$LOG" \
    || launchctl load -w "$plist" 2>>"$LOG" \
    || true
  launchctl enable "$DOMAIN/$label" 2>/dev/null || true
}

kick() {
  local label="$1"
  log "kickstart $label"
  launchctl kickstart -k "$DOMAIN/$label" 2>>"$LOG" || true
}

# tgbot 心跳：进程在但僵死时也要拉起
tgbot_heartbeat_stale() {
  local hb="/tmp/tgbot-dc.heartbeat" age max=120
  [[ -f "$hb" ]] || return 0
  age=$(( $(date +%s) - $(stat -f %m "$hb" 2>/dev/null || echo 0) ))
  (( age > max ))
}

fixed=0

for label in "${KEEPALIVE_LABELS[@]}"; do
  ensure_loaded "$label"
  if ! is_loaded "$label"; then
    log "MISS $label（bootstrap 失败）"
    continue
  fi
  need_kick=0
  if ! has_pid "$label"; then
    need_kick=1
  elif [[ "$label" == "com.dc.tgbot-daemon" ]] && tgbot_heartbeat_stale; then
    log "tgbot 心跳过期，强制 kick"
    need_kick=1
  fi
  if (( need_kick )); then
    kick "$label"
    fixed=$((fixed + 1))
  fi
done

for label in "${LOADED_LABELS[@]}"; do
  ensure_loaded "$label"
  if ! is_loaded "$label"; then
    log "MISS $label（定时项未加载）"
  fi
done

# agent-bus 心跳文件（可选告警，不单独 kick 以免与 KeepAlive 打架）
BUS_HB="${HOME}/Library/Application Support/youchu-agent-bus/state/youchu_ai_poller.heartbeat"
if [[ -f "$BUS_HB" ]]; then
  age=$(( $(date +%s) - $(stat -f %m "$BUS_HB" 2>/dev/null || echo 0) ))
  if (( age > 180 )); then
    log "WARN agent-bus 心跳 ${age}s，kick poller"
    kick com.youchu.agent-bus-poller
    fixed=$((fixed + 1))
  fi
fi

if (( fixed > 0 )); then
  log "OK ensure 完成，拉起 ${fixed} 项"
else
  log "OK ensure 全部在跑"
fi
exit 0
