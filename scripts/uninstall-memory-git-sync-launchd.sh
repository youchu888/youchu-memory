#!/usr/bin/env bash
set -euo pipefail
LABEL=com.youchu.memory-git-sync
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
rm -f "$PLIST"
echo "✓ 已卸载 ${LABEL}"
