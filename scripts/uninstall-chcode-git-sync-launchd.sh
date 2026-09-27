#!/usr/bin/env bash
# 卸载 CHcode 每日 git pull
set -euo pipefail
LABEL="com.youchu.chcode-git-sync"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
DOMAIN="gui/$(id -u)"
launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
rm -f "$PLIST"
echo "OK 已卸载 ${LABEL}"
