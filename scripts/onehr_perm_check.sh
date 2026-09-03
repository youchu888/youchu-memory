#!/usr/bin/env bash
# OneHR 打卡权限自检（屏幕录制 / 辅助功能 / 账号切换）
# 用法：bash ~/.dc-platform/scripts/onehr_perm_check.sh
set -euo pipefail

APP="/Applications/又初打卡截图.app"
CLICK="$HOME/.dc-platform/scripts/onehr_tg_click_account"
HELPER="$HOME/.dc-platform/scripts/onehr_tg_window_info"
LOG_DIR="$HOME/.dc-platform/onehr/logs"
mkdir -p "$LOG_DIR"
OUT="$LOG_DIR/perm_check_$(date +%Y%m%d_%H%M%S).log"

exec > >(tee "$OUT") 2>&1

echo "=== OneHR 权限自检 $(date '+%F %T') ==="
echo

ok=0
warn=0
fail=0

pass() { echo "✅ $*"; ok=$((ok+1)); }
warn() { echo "⚠️  $*"; warn=$((warn+1)); }
bad()  { echo "❌ $*"; fail=$((fail+1)); }

# --- files ---
[[ -d "$APP" ]] && pass "截图 App 存在: $APP" || bad "缺少 $APP"
[[ -x "$CLICK" ]] && pass "账号切换 helper 可执行" || bad "缺少 $CLICK"
[[ -x "$HELPER" ]] && pass "窗口定位 helper 可执行" || bad "缺少 $HELPER"
[[ -d "/Applications/Telegram.app" ]] && pass "Telegram 已安装" || bad "未找到 Telegram.app"

# --- interactive AX ---
TRUST_BIN="/tmp/ax_trust_check"
if [[ ! -x "$TRUST_BIN" ]]; then
  /usr/bin/swiftc -O -o "$TRUST_BIN" - <<'SWIFT' 2>/dev/null || true
import ApplicationServices
print(AXIsProcessTrusted() ? "YES" : "NO")
SWIFT
fi
if [[ -x "$TRUST_BIN" ]]; then
  t="$("$TRUST_BIN" 2>/dev/null || echo NO)"
  if [[ "$t" == *YES* ]]; then
    pass "当前交互进程 辅助功能=YES（Cursor/终端里测）"
  else
    warn "当前交互进程 辅助功能=NO"
  fi
fi

# --- launchd-like AX (the real punch path) ---
echo
echo "--- launchd 等价探测（与今晚打卡同一权限域）---"
PROBE_PY="$HOME/.dc-platform/scripts/_onehr_perm_probe_launchd.py"
cat > "$PROBE_PY" <<'PY'
import subprocess, sys
from pathlib import Path
print("python", sys.executable, flush=True)
r = subprocess.run(["/tmp/ax_trust_check"], capture_output=True, text=True)
print("ax_trust_check", (r.stdout or r.stderr or "").strip(), flush=True)
click = Path.home() / ".dc-platform/scripts/onehr_tg_click_account"
r2 = subprocess.run([str(click), "又初"], capture_output=True, text=True)
print("direct_click_rc", r2.returncode, flush=True)
print("direct_click_err", (r2.stderr or "").strip()[:200], flush=True)
# via Capture App (TCC bundle)
app = Path("/Applications/又初打卡截图.app")
last = Path.home() / ".dc-platform/onehr/last_screenshot.path"
try:
    last.unlink()
except FileNotFoundError:
    pass
# Only test click via a tiny wrapper script launched with open -a? 
# Instead: run click inside app by temporary flag — use open to run full screenshot with --skip-validate for speed? too heavy.
# Minimal: open runs a helper script that only clicks.
helper = Path.home() / ".dc-platform/onehr/logs/_ax_via_app.sh"
helper.write_text(
    "#!/bin/bash\n"
    "set -e\n"
    f"\"{click}\" Ethan; \"{click}\" 又初\n"
    "echo AX_VIA_APP_OK > \"$HOME/.dc-platform/onehr/logs/_ax_via_app.ok\"\n",
    encoding="utf-8",
)
helper.chmod(0o755)
okf = Path.home() / ".dc-platform/onehr/logs/_ax_via_app.ok"
okf.unlink(missing_ok=True)
# Temporarily point app executable? Don't mutate app. Use open with custom — can't.
# Fall back: document that user must grant Accessibility to App; test direct under launchd only.
print("note", "grant Accessibility to 又初打卡截图.app then punch uses open -a", flush=True)
PY

UIDN=$(id -u)
LABEL=com.youchu.onehr-perm-check
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
POUT="$LOG_DIR/perm_launchd_probe.log"
rm -f "$POUT"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>${LABEL}</string>
  <key>EnvironmentVariables</key><dict>
    <key>HOME</key><string>$HOME</string>
    <key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
  </dict>
  <key>ProgramArguments</key><array>
    <string>/usr/local/bin/python3</string>
    <string>-u</string>
    <string>${PROBE_PY}</string>
  </array>
  <key>StandardOutPath</key><string>${POUT}</string>
  <key>StandardErrorPath</key><string>${POUT}</string>
  <key>RunAtLoad</key><true/>
</dict></plist>
EOF
launchctl bootout "gui/${UIDN}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${UIDN}" "$PLIST"
sleep 5
launchctl bootout "gui/${UIDN}/${LABEL}" 2>/dev/null || true
rm -f "$PLIST"
if [[ -f "$POUT" ]]; then
  cat "$POUT"
  if rg -q "direct_click_rc 0" "$POUT"; then
    pass "launchd 直调账号切换：成功"
  else
    bad "launchd 直调账号切换：失败（预期：需给「又初打卡截图」开辅助功能，且打卡经 App 拉起）"
  fi
  if rg -q "ax_trust_check.*NO|trusted=NO" "$POUT"; then
    warn "launchd 进程本身 辅助功能=NO（正常；应靠 App bundle 拿权限）"
  fi
else
  bad "launchd 探测无日志"
fi

# --- Screen Recording TCC ---
echo
echo "--- 屏幕录制 TCC ---"
if sqlite3 "/Library/Application Support/com.apple.TCC/TCC.db" \
  "SELECT client||'='||auth_value FROM access WHERE service='kTCCServiceScreenCapture' AND (client LIKE '%onehr%' OR client LIKE '%python@3.13%');" 2>/dev/null | rg -q "=2"; then
  pass "屏幕录制：python3.13 或 onehr-capture 已授权"
else
  warn "未能从 TCC 读到屏幕录制授权（可能无读权限）；以实截为准"
fi

# --- real screencapture ---
if pgrep -x Telegram >/dev/null; then
  INFO="$("$HELPER" Telegram 2>/dev/null || true)"
  WID="${INFO%%$'\t'*}"
  if [[ -n "$WID" ]]; then
    TESTPNG="$LOG_DIR/perm_screencap_test.png"
    /usr/sbin/screencapture -x -l"$WID" "$TESTPNG" 2>/dev/null || true
    if [[ -s "$TESTPNG" ]]; then
      pass "screencapture 窗口截图成功 ($(wc -c <"$TESTPNG") bytes)"
    else
      bad "screencapture 失败（检查屏幕录制权限）"
    fi
  else
    warn "无法取 Telegram window id"
  fi
else
  warn "Telegram 未运行，跳过截图实测"
fi

echo
echo "=== 你需要手动勾选 ==="
echo "1) 系统设置 → 隐私与安全性 → 辅助功能"
echo "   打开：又初打卡截图（/Applications/又初打卡截图.app）"
echo "2) 系统设置 → 隐私与安全性 → 屏幕录制（若未开）"
echo "   确认：又初打卡截图、以及 python3.13（已有则不动）"
echo
echo "明细日志: $OUT"
echo "汇总: ok=$ok warn=$warn fail=$fail"
exit $(( fail > 0 ? 1 : 0 ))
