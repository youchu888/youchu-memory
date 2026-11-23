#!/usr/bin/env bash
# old-mac：应用私聊 cursor_agent 修复并重新拉起 TG bot（日常权威机）。
# 前置：new-mac 已跑 release-bot-on-new-mac.sh（否则会 409 抢 token）。
# 用法：
#   bash ~/.dc-platform/memory/patches/tgbot-dm-cursor-agent-restore/reclaim-bot-on-old-mac.sh
#   bash .../reclaim-bot-on-old-mac.sh --restart-only
set -euo pipefail

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
RESTART_ONLY=0
[[ "${1:-}" == "--restart-only" ]] && RESTART_ONLY=1

DOMAIN="gui/$(id -u)"
AUTH_FILE="$HOME/.dc-platform/memory/work-log/AUTHORITY_HOST"
HOST_ENV="$HOME/.dc-platform/memory/.env.host"
ROLE_FILE="$HOME/.dc-platform/tgbot-role"
CHCODE="${CHCODE_ROOT:-$HOME/Desktop/CHcode}"

echo "=== 0) 主机提示 ==="
HOST_ID="$(grep -E '^export WORKLOG_HOST_ID=' "$HOST_ENV" 2>/dev/null | cut -d= -f2 || true)"
HOST_ID="${HOST_ID:-unknown}"
echo "  WORKLOG_HOST_ID=${HOST_ID}  CHCODE=$CHCODE"
if [[ ! -d "$CHCODE/omdb/tgbot" ]]; then
  echo "MISS $CHCODE/omdb/tgbot" >&2
  exit 1
fi

echo "=== 1) 私聊模式 → cursor_agent ==="
bash "$PATCH_DIR/restore-dm-cursor-agent.sh"

if [[ "$RESTART_ONLY" -eq 0 ]]; then
  echo "=== 2) 权威 → old-mac + 角色 primary ==="
  mkdir -p "$(dirname "$AUTH_FILE")" "$HOME/.dc-platform/config"
  cat >"$AUTH_FILE" <<'EOF'
# 正式日报权威主机（一行，勿加引号）
# 2026-11-23：TG bot / 自动化权威回到 old-mac
old-mac
EOF
  printf '%s\n' 'export WORKLOG_HOST_ID=old-mac' >"$HOST_ENV"
  printf 'primary\n' >"$ROLE_FILE"
  rm -f "$HOME/.dc-platform/config/DISABLE_LOCAL_AUTOMATION"
fi

echo "=== 3) 部署并启动 TG bot ==="
if [[ -x "$CHCODE/omdb/tgbot/deploy_app_support_runtime.sh" ]]; then
  bash "$CHCODE/omdb/tgbot/deploy_app_support_runtime.sh"
elif [[ -x "$HOME/Library/Application Support/tgbot-dc/scripts/start.sh" ]]; then
  bash "$HOME/Library/Application Support/tgbot-dc/scripts/start.sh"
else
  echo "MISS deploy/start；请手动起 bot" >&2
  exit 1
fi

echo "=== 4) agent-bus（若脚本在）==="
if [[ -x "$CHCODE/.cursor/scripts/sync-agent-bus-deploy.sh" ]]; then
  bash "$CHCODE/.cursor/scripts/sync-agent-bus-deploy.sh" || true
elif [[ -x "$HOME/Library/Application Support/youchu-agent-bus/scripts/start-agent-bus-poller.sh" ]]; then
  bash "$HOME/Library/Application Support/youchu-agent-bus/scripts/start-agent-bus-poller.sh" || true
  bash "$HOME/Library/Application Support/youchu-agent-bus/scripts/start-agent-bus-cursor-executor.sh" || true
fi

echo "=== 5) 自检 ==="
sleep 5
if [[ -f /tmp/tgbot-dc.pid ]] && kill -0 "$(cat /tmp/tgbot-dc.pid)" 2>/dev/null; then
  echo "  bot pid=$(cat /tmp/tgbot-dc.pid)"
else
  echo "  WARN 无 /tmp/tgbot-dc.pid，看 /tmp/tgbot-dc.log" >&2
fi
if [[ -f /tmp/tgbot-dc.log ]]; then
  if grep -q '409 Conflict' /tmp/tgbot-dc.log 2>/dev/null && \
     tail -30 /tmp/tgbot-dc.log | grep -q '409 Conflict'; then
    echo "  WARN 仍有 getUpdates 409：new-mac 或其他实例还在抢，先停对面 bot" >&2
  fi
  if tail -40 /tmp/tgbot-dc.log | grep -q 'Application started'; then
    echo "  OK Application started 可见"
  fi
fi
echo "  role=$(tr -d ' \n' <"$ROLE_FILE" 2>/dev/null || echo '?')"
echo "  authority=$(grep -v '^#' "$AUTH_FILE" 2>/dev/null | head -1 || echo '?')"
echo "DONE old-mac reclaim"
