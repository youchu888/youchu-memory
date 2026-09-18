#!/usr/bin/env bash
# 经 memory-git 在指定主机一次性升级 ToDesk（无需 SSH / 无需 sudo）
# 流程：官方 DMG → 安装器拉 pkg → 截获 pkg → expand → 覆盖 /Applications/ToDesk.app → 重启客户端
# 触发：sync-memory-git.sh / worklog_dual_mac_sync 在 pull 后调用；靠 stamp 幂等
set -euo pipefail

MEM="${MEMORY_GIT_DIR:-$HOME/.dc-platform/memory}"
CFG="$MEM/config/oneshot_upgrade_todesk.env"
STATE_DIR="${HOME}/.dc-platform/state"
STAMP="$STATE_DIR/oneshot_upgrade_todesk.stamp"
LOG="$STATE_DIR/oneshot_upgrade_todesk.log"
WORK="${TMPDIR:-/tmp}/youchu-todesk-upgrade.$$"
DMG_URL_DEFAULT="https://dl.todesk.com/official/ToDesk_Installer.dmg"

mkdir -p "$STATE_DIR"
exec >>"$LOG" 2>&1
echo "==== $(date '+%Y-%m-%d %H:%M:%S') host=$(hostname -s) ===="

_log() { echo "[todesk-upgrade] $*"; }

_host_id() {
  if [[ -f "$MEM/.env.host" ]]; then
    # shellcheck disable=SC1091
    source "$MEM/.env.host"
  fi
  echo "${WORKLOG_HOST_ID:-$(hostname -s)}"
}

_current_version() {
  local app="/Applications/ToDesk.app"
  [[ -d "$app" ]] || { echo ""; return; }
  defaults read "$app/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo ""
}

# 简易版本比较：a >= b → 0
_ver_ge() {
  local a="$1" b="$2"
  [[ -z "$a" ]] && return 1
  [[ "$a" == "$b" ]] && return 0
  local IFS=.
  # shellcheck disable=SC2206
  local aa=($a) bb=($b)
  local i
  for ((i = 0; i < 4; i++)); do
    local x="${aa[i]:-0}" y="${bb[i]:-0}"
    x="${x//[^0-9]/}" y="${y//[^0-9]/}"
    x="${x:-0}" y="${y:-0}"
    ((10#$x > 10#$y)) && return 0
    ((10#$x < 10#$y)) && return 1
  done
  return 0
}

_write_status() {
  local status="$1" detail="${2:-}"
  local host day note
  host="$(_host_id)"
  day="$(date '+%Y-%m-%d')"
  note="$MEM/ops-mirror/hosts/${host}/todesk_upgrade.md"
  mkdir -p "$(dirname "$note")"
  {
    echo "# ToDesk oneshot upgrade · host=\`${host}\`"
    echo
    echo "- time: $(date '+%Y-%m-%d %H:%M:%S %z')"
    echo "- status: **${status}**"
    echo "- detail: ${detail}"
    echo "- before: ${BEFORE_VER:-unknown}"
    echo "- after: $(_current_version)"
  } >"$note"
  # 当日 work-log 一行，便于对端看见
  local wl="$MEM/work-log/hosts/${host}/${day}.md"
  mkdir -p "$(dirname "$wl")"
  touch "$wl"
  if ! grep -q 'ToDesk oneshot' "$wl" 2>/dev/null; then
    echo "- $(date '+%H:%M') ToDesk oneshot: ${status} — ${detail}" >>"$wl"
  fi
}

_cleanup() {
  pkill -f 'ToDesk_Installer' 2>/dev/null || true
  if [[ -n "${MNT:-}" ]]; then
    hdiutil detach "$MNT" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORK" 2>/dev/null || true
}
trap _cleanup EXIT

[[ -f "$CFG" ]] || { _log "no config $CFG — skip"; exit 0; }

# shellcheck disable=SC1090
source "$CFG"

ENABLED="${ENABLED:-0}"
TARGET_HOST="${TARGET_HOST:-old-mac}"
WANT_VERSION="${WANT_VERSION:-4.10.1.0}"
DMG_URL="${DMG_URL:-$DMG_URL_DEFAULT}"
FORCE="${FORCE:-0}"

HOST="$(_host_id)"
BEFORE_VER="$(_current_version)"

if [[ "$ENABLED" != "1" ]]; then
  _log "ENABLED!=1 — skip"
  exit 0
fi

if [[ "$HOST" != "$TARGET_HOST" ]]; then
  _log "host=$HOST != TARGET=$TARGET_HOST — skip"
  exit 0
fi

if [[ -f "$STAMP" && "$FORCE" != "1" ]]; then
  if grep -q '^status=ok' "$STAMP" 2>/dev/null; then
    _log "stamp already ok — skip"
    exit 0
  fi
  # 失败冷却 30 分钟，避免每轮 sync 弹安装器
  if grep -q '^status=fail' "$STAMP" 2>/dev/null; then
    age=99999
    if stat -f%m "$STAMP" >/dev/null 2>&1; then
      age=$(( $(date +%s) - $(stat -f%m "$STAMP") ))
    fi
    if (( age < 1800 )); then
      _log "fail stamp age=${age}s < 1800 — cooldown skip"
      exit 0
    fi
  fi
fi

if [[ "$FORCE" != "1" ]] && _ver_ge "$BEFORE_VER" "$WANT_VERSION"; then
  _log "already $BEFORE_VER >= $WANT_VERSION — stamp ok"
  echo "status=ok" >"$STAMP"
  echo "version=$BEFORE_VER" >>"$STAMP"
  echo "skipped=already_new $(date -Iseconds)" >>"$STAMP"
  _write_status "skipped" "already ${BEFORE_VER} >= ${WANT_VERSION}"
  exit 0
fi

_log "start upgrade host=$HOST before=$BEFORE_VER want=$WANT_VERSION"

mkdir -p "$WORK"
DMG="$WORK/ToDesk_Installer.dmg"
_log "download $DMG_URL"
if ! curl -fsSL --connect-timeout 20 --max-time 600 -o "$DMG" "$DMG_URL"; then
  _write_status "fail" "download DMG failed"
  echo "status=fail" >"$STAMP"
  echo "reason=dmg_download $(date -Iseconds)" >>"$STAMP"
  exit 1
fi

_log "attach DMG"
MNT="$(hdiutil attach -nobrowse -readonly "$DMG" | awk 'END{print $NF}')"
[[ -d "$MNT/ToDesk_Installer.app" ]] || {
  _write_status "fail" "DMG missing ToDesk_Installer.app"
  echo "status=fail" >"$STAMP"
  exit 1
}
cp -R "$MNT/ToDesk_Installer.app" "$WORK/"
hdiutil detach "$MNT" >/dev/null 2>&1 || true
MNT=""

# 清掉旧临时 pkg，避免误判
find "${TMPDIR:-/tmp}" /private/var/folders -maxdepth 4 -name 'ToDesk_*.pkg' -user "$(id -un)" -mmin -120 -delete 2>/dev/null || true

_log "launch installer"
open "$WORK/ToDesk_Installer.app"
sleep 3

_log "try UI: agree + 立即安装"
UI_OK=0
if osascript >/dev/null 2>&1 <<'APPLESCRIPT'
tell application "System Events"
  tell process "ToDesk_Installer"
    set frontmost to true
    delay 0.8
    repeat with i from 1 to 15
      if exists window 1 then exit repeat
      delay 0.5
    end repeat
    if not (exists window 1) then error "no installer window"
    try
      set c to checkbox 1 of window 1
      if value of c is 0 then click c
    end try
    delay 0.3
    click button "立即安装" of window 1
  end tell
end tell
APPLESCRIPT
then
  UI_OK=1
else
  _log "UI automation failed (Accessibility?). Installer left open; waiting for any pkg anyway"
fi

_log "wait for pkg download"
PKG=""
STABLE=0
LAST_SZ=-1
for ((i = 1; i <= 180; i++)); do
  cand="$(find "${TMPDIR:-/tmp}" /private/var/folders -name 'ToDesk_*.pkg' -user "$(id -un)" -mmin -30 2>/dev/null | head -1 || true)"
  if [[ -n "$cand" && -f "$cand" ]]; then
    PKG="$cand"
    sz="$(stat -f%z "$PKG" 2>/dev/null || echo 0)"
    if [[ "$sz" -gt 50000000 && "$sz" == "$LAST_SZ" ]]; then
      STABLE=$((STABLE + 1))
    else
      STABLE=0
    fi
    LAST_SZ="$sz"
    if ((STABLE >= 3)); then
      _log "pkg ready: $PKG ($sz bytes)"
      break
    fi
    if ((i % 5 == 0)); then
      _log "downloading… t=${i}s size=$sz"
    fi
  fi
  sleep 2
done

pkill -f 'ToDesk_Installer' 2>/dev/null || true
sleep 1

if [[ -z "$PKG" || ! -f "$PKG" ]]; then
  _write_status "fail" "pkg not downloaded (UI/Accessibility?); installer may be waiting on screen"
  echo "status=fail" >"$STAMP"
  echo "reason=no_pkg $(date -Iseconds)" >>"$STAMP"
  # 保底：把安装器放到用户能点的位置
  cp -R "$WORK/ToDesk_Installer.app" "$HOME/Downloads/ToDesk_Installer.app" 2>/dev/null || true
  open "$HOME/Downloads/ToDesk_Installer.app" 2>/dev/null || true
  exit 1
fi

KEEP="$WORK/ToDesk_captured.pkg"
cp -f "$PKG" "$KEEP"
_log "expand pkg"
EXPAND="$WORK/expand"
rm -rf "$EXPAND"
pkgutil --expand "$KEEP" "$EXPAND"
PAYLOAD="$EXPAND/ToDesk.pkg/Payload"
[[ -f "$PAYLOAD" ]] || {
  _write_status "fail" "Payload missing in pkg"
  echo "status=fail" >"$STAMP"
  exit 1
}

_log "extract Payload"
PAYDIR="$WORK/payload"
mkdir -p "$PAYDIR"
(cd "$PAYDIR" && gzip -dc "$PAYLOAD" | cpio -id 2>/dev/null)
NEW_APP="$PAYDIR/Applications/ToDesk.app"
[[ -d "$NEW_APP" ]] || {
  _write_status "fail" "extracted app missing"
  echo "status=fail" >"$STAMP"
  exit 1
}
NEW_VER="$(defaults read "$NEW_APP/Contents/Info" CFBundleShortVersionString 2>/dev/null || echo unknown)"
_log "extracted version=$NEW_VER"

_log "quit running ToDesk"
osascript -e 'tell application "ToDesk" to quit' 2>/dev/null || true
pkill -x ToDesk 2>/dev/null || true
pkill -x ToDesk_Service 2>/dev/null || true
pkill -f 'ToDesk.app' 2>/dev/null || true
sleep 2

_log "replace /Applications/ToDesk.app"
DEST="/Applications/ToDesk.app"
BAK="/Applications/ToDesk.app.youchu-bak.$$"
if [[ -d "$DEST" ]]; then
  # 目录对用户可写时可直接挪走（含 root 拥有的二进制）
  if ! mv "$DEST" "$BAK" 2>/dev/null; then
    _write_status "fail" "cannot move existing ToDesk.app (permission)"
    echo "status=fail" >"$STAMP"
    exit 1
  fi
fi
if ! mv "$NEW_APP" "$DEST"; then
  _log "restore bak"
  [[ -d "$BAK" ]] && mv "$BAK" "$DEST" || true
  _write_status "fail" "cannot install new ToDesk.app"
  echo "status=fail" >"$STAMP"
  exit 1
fi
rm -rf "$BAK" 2>/dev/null || true

_log "launch ToDesk"
open -a ToDesk || open "$DEST"
sleep 5
AFTER="$(_current_version)"
_log "after=$AFTER"

if _ver_ge "$AFTER" "$WANT_VERSION"; then
  echo "status=ok" >"$STAMP"
  echo "version=$AFTER" >>"$STAMP"
  echo "finished=$(date -Iseconds)" >>"$STAMP"
  _write_status "ok" "upgraded ${BEFORE_VER:-none} → ${AFTER}"
  _log "SUCCESS $BEFORE_VER → $AFTER"
  exit 0
fi

_write_status "warn" "replaced but version read=$AFTER want=$WANT_VERSION"
echo "status=warn" >"$STAMP"
echo "version=$AFTER" >>"$STAMP"
exit 0
