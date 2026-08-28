#!/usr/bin/env bash
set -euo pipefail
LABEL="com.youchu.onehr-checkin"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
rm -f "$PLIST"
echo "OK 已卸载 ${LABEL}"
