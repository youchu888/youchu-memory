#!/usr/bin/env python3
"""OneHR 考勤自动打卡：登录 → 检测开放时段 → 上传 Telegram 设备截图（或休息段确认）。

依赖：~/.dc-platform/config/onehr.env（chmod 600）
截图：~/.dc-platform/scripts/onehr_telegram_devices_screenshot.sh
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

DEFAULT_ENV = Path.home() / ".dc-platform/config/onehr.env"
DEFAULT_SCREENSHOT_SCRIPT = Path.home() / ".dc-platform/scripts/onehr_telegram_devices_screenshot.sh"
DEFAULT_LOG_DIR = Path.home() / ".dc-platform/onehr/logs"
STATE_FILE = Path.home() / ".dc-platform/onehr/state.json"
SCHEDULE_STATE_FILE = Path.home() / ".dc-platform/onehr/schedule_state.json"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def load_env(path: Path) -> Dict[str, str]:
    if not path.is_file():
        raise SystemExit(f"缺少配置文件 {path}（可复制 onehr.env.example）")
    env: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def log(msg: str, log_file: Optional[Path] = None) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def _load_tgbot_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    for path in (
        Path.home() / "Desktop/CHcode/omdb/tgbot/.env",
        Path("/Users/mac/Desktop/CHcode/omdb/tgbot/.env"),
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip('"').strip("'")
        break
    return env


def notify_tg(title: str, message: str) -> None:
    """打卡结果推到主人 TG 私聊（时间 + 成功/失败）。"""
    env = _load_tgbot_env()
    token = env.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN") or ""
    raw_users = env.get("ALLOWED_USERS") or os.environ.get("ALLOWED_USERS") or ""
    uids = [int(x) for x in re.split(r"[,\s]+", raw_users) if x.strip().isdigit()]
    if not token or not uids:
        return
    now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    text = f"{title}\n时间: {now}（Asia/Shanghai）\n{message}"
    body = json.dumps({"chat_id": uids[0], "text": text}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read()
    except Exception as exc:  # noqa: BLE001 — 通知失败不挡打卡主流程
        print(f"[warn] TG 通知失败: {exc}", flush=True)


def notify(title: str, message: str) -> None:
    safe_title = title.replace('"', '\\"')
    safe_msg = message.replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe_msg}" with title "{safe_title}"'],
        check=False,
        capture_output=True,
    )
    notify_tg(title, message)


def api_json(
    method: str,
    url: str,
    token: Optional[str] = None,
    body: Optional[dict] = None,
) -> Tuple[int, Any]:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {"error": exc.reason}
        except json.JSONDecodeError:
            payload = {"error": raw.decode("utf-8", errors="replace") or exc.reason}
        return exc.code, payload


def api_multipart(
    url: str,
    token: str,
    fields: Dict[str, str],
    file_field: str,
    file_path: Path,
) -> Tuple[int, Any]:
    boundary = f"----OneHR{int(datetime.now().timestamp() * 1000)}"
    body_parts: List[bytes] = []

    for name, value in fields.items():
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )

    file_bytes = file_path.read_bytes()
    filename = file_path.name
    body_parts.append(
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode("utf-8")
        + file_bytes
        + b"\r\n"
    )
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(body_parts)

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode("utf-8")) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {"error": exc.reason}
        except json.JSONDecodeError:
            payload = {"error": raw.decode("utf-8", errors="replace") or exc.reason}
        return exc.code, payload


def login(base_url: str, employee_code: str, password: str) -> str:
    status, payload = api_json(
        "POST",
        f"{base_url.rstrip('/')}/api/auth/login",
        body={"employee_code": employee_code, "password": password},
    )
    if status != 200 or not isinstance(payload, dict) or not payload.get("token"):
        raise RuntimeError(f"登录失败 HTTP {status}: {payload}")
    return payload["token"]


def fetch_today(base_url: str, token: str) -> dict:
    status, payload = api_json("GET", f"{base_url.rstrip('/')}/api/checkin/today", token=token)
    if status != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"获取今日打卡失败 HTTP {status}: {payload}")
    return payload


MAX_FRESH_SCREENSHOT_SEC = 180
VALIDATE_BIN = Path.home() / ".dc-platform/scripts/onehr_tg_screenshot_validate"
VALIDATE_SRC = Path.home() / ".dc-platform/scripts/onehr_tg_screenshot_validate.swift"


def screenshot_age_sec(path: Path) -> float:
    return max(0.0, time.time() - path.stat().st_mtime)


def ensure_validate_bin() -> Path:
    """编译 Vision 校验 helper（若源码更新）。"""
    if not VALIDATE_SRC.is_file():
        raise RuntimeError(f"缺少校验源码: {VALIDATE_SRC}")
    need = (not VALIDATE_BIN.is_file()) or (
        VALIDATE_SRC.stat().st_mtime > VALIDATE_BIN.stat().st_mtime
    )
    if need:
        proc = subprocess.run(
            ["/usr/bin/swiftc", "-O", "-o", str(VALIDATE_BIN), str(VALIDATE_SRC)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"编译校验 helper 失败: {proc.stderr.strip()}")
    return VALIDATE_BIN


def validate_devices_screenshot(path: Path) -> str:
    """确认 PNG 是 Telegram 设备管理页，不是聊天壁纸/风景图。返回校验摘要。"""
    if not path.is_file():
        raise RuntimeError(f"截图不存在: {path}")
    bin_path = ensure_validate_bin()
    proc = subprocess.run([str(bin_path), str(path)], capture_output=True, text=True)
    detail = (proc.stdout or proc.stderr or "").strip()
    if proc.returncode != 0:
        raise RuntimeError(detail or f"截图内容校验失败 path={path}")
    return detail or "OK"


def latest_screenshot(
    screenshot_dir: Path,
    max_age_sec: int = MAX_FRESH_SCREENSHOT_SEC,
) -> Optional[Path]:
    """只接受刚截出来的、且内容校验通过的图。禁止拿目录里几天前的旧 PNG 顶上去。"""
    if not screenshot_dir.is_dir():
        return None
    files = sorted(screenshot_dir.glob("telegram_devices_*.png"), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    newest = files[-1]
    age = screenshot_age_sec(newest)
    if age > max_age_sec:
        return None
    try:
        validate_devices_screenshot(newest)
    except RuntimeError:
        return None
    return newest


def _take_screenshot_once(script: Path, capture_only: bool = False) -> Path:
    if not script.is_file():
        raise RuntimeError(f"截图脚本不存在: {script}")
    cmd = [str(script)]
    if capture_only:
        cmd.append("--capture-only")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "截图脚本失败")
    for line in proc.stdout.splitlines():
        if line.startswith("OK "):
            path = Path(line[3:].strip())
            if path.is_file():
                return path
    m = re.search(r"(/\S+\.png)", proc.stdout)
    if m and Path(m.group(1)).is_file():
        return Path(m.group(1))
    raise RuntimeError(f"无法解析截图路径:\n{proc.stdout}\n{proc.stderr}")


def take_screenshot(script: Path, capture_only: bool = False, retries: int = 3) -> Path:
    """截图并校验内容。重试时默认重新导航设备页（不用 capture-only），避免截到聊天壁纸。"""
    last_err = "截图失败"
    for attempt in range(1, retries + 1):
        try:
            # 仅当调用方显式要求时才 capture-only；失败重试必须重新 deeplink
            path = _take_screenshot_once(script, capture_only=capture_only)
            age = screenshot_age_sec(path)
            if age > MAX_FRESH_SCREENSHOT_SEC:
                last_err = f"截到的文件过旧 age={int(age)}s path={path}"
            else:
                # bash 脚本已校验；再防一层（例如 --screenshot 手工传入）
                validate_devices_screenshot(path)
                return path
        except RuntimeError as exc:
            last_err = str(exc)
        if attempt < retries:
            time.sleep(2.0)
    raise RuntimeError(last_err)


def load_state() -> dict:
    if STATE_FILE.is_file():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def slot_label(slot: dict) -> str:
    kind = slot.get("kind", "?")
    idx = slot.get("index", "?")
    return f"slot#{idx}({kind}) {slot.get('from', '?')}-{slot.get('to', '?')}"


def submit_slot(
    base_url: str,
    token: str,
    business_date: str,
    slot: dict,
    screenshot: Optional[Path],
) -> Tuple[int, Any]:
    url = f"{base_url.rstrip('/')}/api/checkin/records"
    idx = str(slot["index"])
    kind = slot.get("kind", "")

    if kind == "break":
        body = {"slot_index": slot["index"], "source": "app", "business_date": business_date}
        return api_json("POST", url, token=token, body=body)

    if not screenshot or not screenshot.is_file():
        raise RuntimeError("需要截图但未提供有效文件")

    fields = {"slot_index": idx, "business_date": business_date}
    return api_multipart(url, token, fields, "screenshot", screenshot)


def slot_done_for_kind(today: dict, kind_filter: Optional[str]) -> bool:
    if not kind_filter:
        return False
    for slot in today.get("slots") or []:
        if kind_filter == "checkin" and slot.get("kind") == "in" and slot.get("status") == "done":
            return True
        if kind_filter == "checkout" and slot.get("kind") == "out" and slot.get("status") == "done":
            return True
    return False


def pick_due_slots(
    today: dict,
    force_index: Optional[int] = None,
    kind_filter: Optional[str] = None,
) -> List[dict]:
    slots = today.get("slots") or []
    if force_index is not None:
        for slot in slots:
            if slot.get("index") == force_index:
                return [slot]
        raise RuntimeError(f"未找到 slot_index={force_index}")
    due = [s for s in slots if s.get("status") == "due"]
    if kind_filter == "checkin":
        due = [s for s in due if s.get("kind") == "in"]
    elif kind_filter == "checkout":
        due = [s for s in due if s.get("kind") == "out"]
    return due


def is_sunday_beijing() -> bool:
    return datetime.now(ZoneInfo("Asia/Shanghai")).weekday() == 6


def sync_schedule_state(today: dict) -> None:
    """将服务端已打卡状态同步到调度 state（避免误报遗漏）。"""
    today_d = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    sched: dict = {}
    if SCHEDULE_STATE_FILE.is_file():
        try:
            sched = json.loads(SCHEDULE_STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    changed = False
    if slot_done_for_kind(today, "checkin") and sched.get("checkin") != today_d:
        sched["checkin"] = today_d
        changed = True
    if slot_done_for_kind(today, "checkout") and sched.get("checkout") != today_d:
        sched["checkout"] = today_d
        changed = True
    if changed:
        SCHEDULE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SCHEDULE_STATE_FILE.write_text(json.dumps(sched, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="OneHR 自动打卡")
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--dry-run", action="store_true", help="只检测开放时段，不截图不上传")
    parser.add_argument("--force-slot", type=int, help="强制指定 slot_index（忽略 status）")
    parser.add_argument("--screenshot", type=Path, help="使用已有截图，不重新截")
    parser.add_argument("--skip-screenshot", action="store_true", help="休息段 break 打卡用")
    parser.add_argument("--kind", choices=("checkin", "checkout"), help="仅处理上班 in / 下班 out")
    parser.add_argument("--capture-only", action="store_true", help="截图时不导航，只截当前 Telegram 窗口")
    parser.add_argument("--sync-schedule", action="store_true", help="仅同步服务端已打卡状态到调度器")
    args = parser.parse_args()

    cfg = load_env(args.env)
    base_url = cfg.get("ONEHR_BASE_URL", "https://m-reportsys.cc")
    employee_code = cfg.get("ONEHR_EMPLOYEE_CODE", "")
    password = cfg.get("ONEHR_PASSWORD", "")
    screenshot_dir = Path(cfg.get("ONEHR_SCREENSHOT_DIR", str(Path.home() / "Desktop/CH/telegram")))
    screenshot_script = Path(cfg.get("ONEHR_SCREENSHOT_SCRIPT", str(DEFAULT_SCREENSHOT_SCRIPT)))
    log_dir = Path(cfg.get("ONEHR_LOG_DIR", str(DEFAULT_LOG_DIR)))
    log_file = log_dir / f"checkin_{datetime.now():%Y%m%d}.log"

    if not employee_code or not password:
        raise SystemExit("ONEHR_EMPLOYEE_CODE / ONEHR_PASSWORD 未配置")

    log(f"开始 OneHR 自动打卡 dry_run={args.dry_run}", log_file)

    if is_sunday_beijing() and args.force_slot is None:
        log("周日无打卡安排，退出", log_file)
        return 0

    token = login(base_url, employee_code, password)
    today = fetch_today(base_url, token)

    if args.sync_schedule:
        sync_schedule_state(today)
        log("已同步调度状态", log_file)
        return 0

    business_date = today.get("business_date", "")
    tz = today.get("timezone", "Asia/Shanghai")
    log(f"business_date={business_date} timezone={tz} shift={today.get('shift_name', '')}", log_file)

    due_slots = pick_due_slots(today, args.force_slot, args.kind)
    if not due_slots:
        if slot_done_for_kind(today, args.kind):
            sync_schedule_state(today)
            log(f"服务端已打卡（kind={args.kind}），无需重复提交", log_file)
            return 0
        log(f"当前无开放打卡时段（status=due kind={args.kind or 'any'}），退出", log_file)
        return 2

    state = load_state()
    rc = 0
    submitted = False

    for slot in due_slots:
        label = slot_label(slot)
        kind = slot.get("kind", "")
        state_key = f"{business_date}:{slot.get('index')}"

        if slot.get("status") == "done" and args.force_slot is None:
            log(f"跳过已打卡 {label}", log_file)
            continue

        if state.get(state_key) and args.force_slot is None:
            log(f"跳过本机已记录成功 {label} @ {state.get(state_key)}", log_file)
            continue

        needs_shot = kind != "break"

        log(f"处理 {label} status={slot.get('status')} needs_screenshot={needs_shot}", log_file)

        if args.dry_run:
            log(f"[dry-run] 将提交 {label}", log_file)
            continue

        screenshot_path: Optional[Path] = args.screenshot
        if needs_shot and not args.skip_screenshot:
            if screenshot_path is None:
                try:
                    screenshot_path = take_screenshot(screenshot_script, capture_only=args.capture_only)
                    log(
                        f"截图完成 {screenshot_path} age={int(screenshot_age_sec(screenshot_path))}s",
                        log_file,
                    )
                except RuntimeError as exc:
                    log(f"截图失败，不使用过期旧图: {exc}", log_file)
                    screenshot_path = latest_screenshot(screenshot_dir)
                    if screenshot_path is not None:
                        log(
                            f"使用刚截出的文件 {screenshot_path} "
                            f"age={int(screenshot_age_sec(screenshot_path))}s",
                            log_file,
                        )
            if screenshot_path is None:
                msg = f"无法获取新鲜截图 {label}（拒绝上传超过 {MAX_FRESH_SCREENSHOT_SEC}s 的旧图）"
                log(f"ERROR {msg}", log_file)
                notify("OneHR 打卡失败", msg)
                rc = 1
                continue
            age = int(screenshot_age_sec(screenshot_path))
            if age > MAX_FRESH_SCREENSHOT_SEC and args.screenshot is None:
                msg = f"截图过旧 age={age}s path={screenshot_path}"
                log(f"ERROR {msg}", log_file)
                notify("OneHR 打卡失败", msg)
                rc = 1
                continue
            try:
                vdetail = validate_devices_screenshot(screenshot_path)
                log(f"截图内容校验通过 {vdetail}", log_file)
            except RuntimeError as exc:
                msg = f"截图内容不是设备管理页，拒绝上传: {exc}"
                log(f"ERROR {msg}", log_file)
                notify("OneHR 打卡失败", msg[:120])
                rc = 1
                continue
            log(f"将上传截图 {screenshot_path} age={age}s", log_file)

        try:
            status, payload = submit_slot(base_url, token, business_date, slot, screenshot_path)
        except RuntimeError as exc:
            log(f"ERROR 提交异常 {label}: {exc}", log_file)
            notify("OneHR 打卡失败", str(exc)[:120])
            rc = 1
            continue

        if 200 <= status < 300:
            now = datetime.now(timezone.utc).isoformat()
            state[state_key] = now
            save_state(state)
            submitted = True
            sync_schedule_state(today)
            log(f"OK 打卡成功 {label} HTTP {status}", log_file)
            notify("OneHR 打卡成功", label)
        else:
            err = payload.get("error") if isinstance(payload, dict) else str(payload)
            log(f"ERROR 打卡失败 {label} HTTP {status}: {err}", log_file)
            notify("OneHR 打卡失败", f"{label}: {err}"[:120])
            rc = 1

    if submitted:
        return 0
    if slot_done_for_kind(today, args.kind):
        return 0
    if due_slots and rc == 0:
        log("无实际提交（均已跳过）", log_file)
        return 2
    return rc


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
