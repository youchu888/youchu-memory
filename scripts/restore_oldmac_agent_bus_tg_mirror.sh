#!/usr/bin/env bash
# old-mac：恢复「狂人 bus 原文 → TG 私聊」镜像链
#
# 链路：poller queue_incoming_tg → youchu_ai_tg_status.jsonl(type=incoming)
#       → tgbot agent_bus_tg_mirror → 主人私聊
#
# 用法（只在旧 Mac 跑）：
#   bash ~/.dc-platform/memory/scripts/restore_oldmac_agent_bus_tg_mirror.sh
#   # 或 memory sync 后：
#   bash ~/.dc-platform/memory/scripts/restore_oldmac_agent_bus_tg_mirror.sh --force
#
# 新 Mac 禁止跑（会抢主控）；脚本默认拒绝 WORKLOG_HOST_ID=new-mac。
set -euo pipefail

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force|-f) FORCE=1 ;;
    -h|--help)
      sed -n '2,20p' "$0"
      exit 0
      ;;
  esac
done

HOST_ID="${WORKLOG_HOST_ID:-}"
if [[ "$HOST_ID" == "new-mac" && "$FORCE" -ne 1 ]]; then
  echo "[fail] 本机 WORKLOG_HOST_ID=new-mac。私聊镜像只由 old-mac 跑。" >&2
  echo "       请到旧 Mac 执行本脚本；若确认要在本机抢主控，加 --force。" >&2
  exit 2
fi
if [[ -z "$HOST_ID" ]]; then
  echo "[warn] WORKLOG_HOST_ID 未设；按 old-mac 主控继续。建议: export WORKLOG_HOST_ID=old-mac"
fi

BUS_ROOT="${AGENT_BUS_ROOT:-$HOME/Library/Application Support/youchu-agent-bus}"
BUS_SCRIPTS="${AGENT_BUS_SCRIPTS:-$BUS_ROOT/scripts}"
STATE_DIR="${AGENT_BUS_STATE_DIR:-$BUS_ROOT/state}"
TGBOT_DIR="${TGBOT_DIR:-$HOME/Desktop/CHcode/omdb/tgbot}"
CHCODE_ROOT="${CHCODE_ROOT:-$HOME/Desktop/CHcode}"
PYTHON3="/opt/homebrew/bin/python3"
[[ -x "$PYTHON3" ]] || PYTHON3="$(command -v python3)"

export AGENT_BUS_STATE_DIR="$STATE_DIR"
export WORKLOG_HOST_ID="${HOST_ID:-old-mac}"

echo "=== restore agent-bus TG mirror (old-mac) ==="
echo "[info] host_id=$WORKLOG_HOST_ID"
echo "[info] state=$STATE_DIR"
echo "[info] tgbot=$TGBOT_DIR"
echo "[info] bus_scripts=$BUS_SCRIPTS"

need_dir() {
  local d="$1"
  if [[ ! -d "$d" ]]; then
    echo "[fail] missing dir: $d" >&2
    exit 1
  fi
}
need_dir "$STATE_DIR"
need_dir "$TGBOT_DIR"
if [[ ! -d "$BUS_SCRIPTS" ]]; then
  # 回退到仓内脚本
  BUS_SCRIPTS="$CHCODE_ROOT/.cursor/scripts"
  need_dir "$BUS_SCRIPTS"
  echo "[warn] App Support scripts 缺失，改用 $BUS_SCRIPTS"
fi

echo
echo "--- 1/4 stop stray new-mac-style duplicates (safe) ---"
# 不杀旧机该有的进程；只清明显僵尸 pidfile
if [[ -f "$STATE_DIR/poller.pid" ]]; then
  old="$(cat "$STATE_DIR/poller.pid" 2>/dev/null || true)"
  if [[ -n "${old:-}" ]] && ! kill -0 "$old" 2>/dev/null; then
    rm -f "$STATE_DIR/poller.pid"
    echo "[ok] cleared stale poller.pid"
  fi
fi

echo
echo "--- 2/4 restart TG bot (status_mirror) ---"
# 先停守护/监控，避免与 restart 抢杀刚拉起的 bot（SIGTERM 15 常见根因）
if [[ -x "$TGBOT_DIR/stop_daemon.sh" ]]; then
  bash "$TGBOT_DIR/stop_daemon.sh" 2>/dev/null || true
fi
if [[ -x "$TGBOT_DIR/stop_monitor.sh" ]]; then
  bash "$TGBOT_DIR/stop_monitor.sh" 2>/dev/null || true
fi
UID_NUM="$(id -u)"
for label in com.youchu.tgbot-dc com.dc.tgbot-daemon com.youchu.tgbot-daemon; do
  launchctl bootout "gui/${UID_NUM}/${label}" 2>/dev/null || true
done
if [[ -x "$TGBOT_DIR/stop.sh" ]]; then
  bash "$TGBOT_DIR/stop.sh" 2>/dev/null || true
fi
pkill -f 'python.*omdb/tgbot/bot\.py' 2>/dev/null || true
pkill -f 'python.*tgbot/bot\.py' 2>/dev/null || true
rm -f /tmp/tgbot-dc.pid /tmp/tgbot-dc.heartbeat
sleep 3
if [[ -x "$TGBOT_DIR/start.sh" ]]; then
  bash "$TGBOT_DIR/start.sh"
else
  echo "[fail] tgbot start.sh 不存在: $TGBOT_DIR" >&2
  exit 1
fi
sleep 3
if [[ ! -f /tmp/tgbot-dc.pid ]] || ! kill -0 "$(cat /tmp/tgbot-dc.pid)" 2>/dev/null; then
  echo "[fail] tgbot 启动失败，最近日志：" >&2
  tail -n 80 /tmp/tgbot-dc.log 2>/dev/null || true
  exit 1
fi
echo "[ok] tgbot pid=$(cat /tmp/tgbot-dc.pid)"
# bot 起来后再开守护（避免启动窗口内互相 restart）
if [[ -x "$TGBOT_DIR/start_daemon_bg.sh" ]]; then
  bash "$TGBOT_DIR/start_daemon_bg.sh" 2>/dev/null || true
elif [[ -x "$TGBOT_DIR/start_daemon.sh" ]]; then
  nohup bash "$TGBOT_DIR/start_daemon.sh" >>/tmp/tgbot-dc-daemon.log 2>&1 &
  echo $! >/tmp/tgbot-dc-daemon.pid
  echo "[ok] tgbot daemon bg pid=$!"
fi

echo
echo "--- 3/4 start poller + wake-bridge + daemon ---"
# 顺序：poller → wake-bridge → daemon（daemon 会盯 poller 掉线）
if [[ -x "$BUS_SCRIPTS/start-agent-bus-poller.sh" ]]; then
  bash "$BUS_SCRIPTS/start-agent-bus-poller.sh"
else
  echo "[fail] start-agent-bus-poller.sh 不存在" >&2
  exit 1
fi
if [[ -x "$BUS_SCRIPTS/start-agent-bus-wake-bridge.sh" ]]; then
  bash "$BUS_SCRIPTS/start-agent-bus-wake-bridge.sh" || true
fi
if [[ -x "$BUS_SCRIPTS/start-agent-bus-daemon-bg.sh" ]]; then
  bash "$BUS_SCRIPTS/start-agent-bus-daemon-bg.sh" || true
elif [[ -x "$BUS_SCRIPTS/start-agent-bus-daemon.sh" ]]; then
  # 前台脚本：用 bg 包装
  nohup bash "$BUS_SCRIPTS/start-agent-bus-daemon.sh" >>"$STATE_DIR/daemon-bg.log" 2>&1 &
  echo $! >"$STATE_DIR/daemon-bg.pid"
  echo "[ok] daemon bg pid=$!"
fi

# LaunchAgent：只踢 poller；tgbot 已手工拉起，避免 kickstart 再杀一轮
UID_NUM="$(id -u)"
if [[ -f "$HOME/Library/LaunchAgents/com.youchu.agent-bus-poller.plist" ]]; then
  launchctl kickstart -k "gui/${UID_NUM}/com.youchu.agent-bus-poller" 2>/dev/null \
    && echo "[ok] launchctl kickstart com.youchu.agent-bus-poller" \
    || echo "[warn] launchctl kickstart poller 失败（可忽略若手工已起）"
fi

echo
echo "--- 4/4 verify ---"
fail=0
check_proc() {
  local pat="$1" label="$2"
  if pgrep -f "$pat" >/dev/null 2>&1; then
    echo "[ok] $label running: $(pgrep -f "$pat" | tr '\n' ' ')"
  else
    echo "[fail] $label NOT running (pattern=$pat)" >&2
    fail=1
  fi
}
check_proc 'agent_bus_poll.py' 'poller'
check_proc 'omdb/tgbot/bot.py|tgbot/bot.py' 'tgbot'
# wake-bridge 非私聊镜像硬依赖，缺了只警告
if pgrep -f 'wake.bridge|wake_bridge|start-agent-bus-wake|agent_bus_wake' >/dev/null 2>&1; then
  echo "[ok] wake-bridge running"
else
  echo "[warn] wake-bridge 未检测到（Cursor 唤醒可能受影响；私聊镜像仍可只用 poller+bot）"
fi

STATUS="$STATE_DIR/youchu_ai_tg_status.jsonl"
CUTOFF_F="$STATE_DIR/youchu_ai_incoming_tg_cutoff"
OFFSET_F="$STATE_DIR/youchu_ai.offset"
echo "[info] offset=$(cat "$OFFSET_F" 2>/dev/null || echo '?') cutoff=$(cat "$CUTOFF_F" 2>/dev/null || echo '?')"
if [[ -f "$STATUS" ]]; then
  AGENT_BUS_TG_STATUS_PATH="$STATUS" "$PYTHON3" - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ["AGENT_BUS_TG_STATUS_PATH"])
last_in = last_any = None
for line in p.read_text(errors="ignore").splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        o = json.loads(line)
    except Exception:
        continue
    last_any = o
    if o.get("type") == "incoming":
        last_in = o
print("[info] tg_status last event:", (last_any or {}).get("ts"), (last_any or {}).get("type"), (last_any or {}).get("bus_id"))
print("[info] last incoming:", (last_in or {}).get("ts"), "bus", (last_in or {}).get("bus_id"))
if last_in is None:
    print("[warn] 尚无 incoming 记录属历史问题；恢复后看「下一条新狂人消息」是否进私聊")
PY
else
  echo "[warn] missing $STATUS"
fi

if [[ -x "$BUS_SCRIPTS/agent-bus-poller-check.sh" ]]; then
  echo
  echo "--- poller-check ---"
  AGENT_BUS_STATE_DIR="$STATE_DIR" bash "$BUS_SCRIPTS/agent-bus-poller-check.sh" 2>&1 | head -30 || true
elif [[ -x "$CHCODE_ROOT/.cursor/scripts/agent-bus-poller-check.sh" ]]; then
  echo
  echo "--- poller-check ---"
  AGENT_BUS_STATE_DIR="$STATE_DIR" bash "$CHCODE_ROOT/.cursor/scripts/agent-bus-poller-check.sh" 2>&1 | head -30 || true
fi

echo
if [[ "$fail" -eq 0 ]]; then
  echo "[DONE] 进程已起。历史积压不会回灌私聊（避免刷屏）；"
  echo "       请等狂人下一条新 bus，或让狂人发一条短测，看私聊是否出现 type=incoming。"
  echo "自检: tail -5 \"$STATUS\""
  exit 0
fi
echo "[DONE-WITH-FAILS] 有进程未起来，看上方 [fail] 与 /tmp/tgbot-dc.log / $STATE_DIR/poller.log" >&2
exit 1
