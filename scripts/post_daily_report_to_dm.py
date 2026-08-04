#!/usr/bin/env python3
"""日报定稿后推送到 TG 机器人私聊（canonical · 经 youchu-memory 同步到双机）。

默认仅权威主机 old-mac 可实发；new-mac 会跳过。

用法（旧 Mac 21:30 定稿后）:
  python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py
  python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py --date YYYY-MM-DD
  python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py --dry-run
  python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py --force
  python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py --allow-non-authority
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
MEMORY_ROOT = Path.home() / ".dc-platform" / "memory"
MEMORY_REPORTS = MEMORY_ROOT / "work-log" / "reports"
LOCAL_REPORTS = Path.home() / "Desktop" / "CHcode" / ".cursor" / "work-log" / "reports"
MARKER_PATH = MEMORY_ROOT / "work-log" / "reports" / ".daily_report_dm_posted.json"


def _find_tgbot_dir() -> Path:
    candidates = [
        Path.home() / "Desktop" / "CHcode" / "omdb" / "tgbot",
        Path("/Users/mac/Desktop/CHcode/omdb/tgbot"),
    ]
    for p in candidates:
        if (p / ".env").is_file():
            return p
    return candidates[0]


TGBOT_DIR = _find_tgbot_dir()


def _load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("'\"")
    return out


def _tg_creds() -> tuple[str, list[int]]:
    env = _load_env_file(TGBOT_DIR / ".env")
    token = os.environ.get("TG_BOT_TOKEN") or env.get("TG_BOT_TOKEN") or ""
    raw = os.environ.get("ALLOWED_USERS") or env.get("ALLOWED_USERS") or ""
    users = [int(x) for x in re.split(r"[,\s]+", raw) if x.strip().isdigit()]
    return token, users


def split_for_telegram(text: str, *, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    buf = ""
    for line in text.splitlines(keepends=True):
        if len(buf) + len(line) > limit and buf:
            parts.append(buf.rstrip())
            buf = line
        else:
            buf += line
    if buf.strip():
        parts.append(buf.rstrip())
    return parts or [text[:limit]]


def _today() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def _candidate_paths(day: str) -> list[Path]:
    names = [f"{day}-日报.md", f"日报-{day}.md"]
    out: list[Path] = []
    for root in (MEMORY_REPORTS, LOCAL_REPORTS):
        for name in names:
            out.append(root / name)
    return out


def resolve_report(day: str, file: str | None) -> Path:
    if file:
        p = Path(file).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"report file not found: {p}")
        return p
    for p in _candidate_paths(day):
        if p.is_file() and p.stat().st_size > 0:
            return p
    tried = "\n".join(f"  - {p}" for p in _candidate_paths(day))
    raise FileNotFoundError(f"no daily report for {day}. tried:\n{tried}")


def _load_marker() -> dict:
    if not MARKER_PATH.exists():
        return {}
    try:
        return json.loads(MARKER_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_marker(data: dict) -> None:
    MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKER_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def already_posted(day: str) -> bool:
    return bool(_load_marker().get(day))


def mark_posted(day: str, *, chat_ids: list[int], path: str) -> None:
    data = _load_marker()
    data[day] = {
        "posted_at": datetime.now(TZ).isoformat(timespec="seconds"),
        "chat_ids": chat_ids,
        "path": path,
        "host": _worklog_host_id() or "unknown",
    }
    _save_marker(data)


def send_text(token: str, chat_id: int, text: str) -> dict:
    if not token:
        raise RuntimeError("TG_BOT_TOKEN empty")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = json.dumps(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_payload(day: str, body: str) -> str:
    return f"📋 又初 · 日报 {day}\n（定稿自动推送）\n\n{body.strip()}\n"


def _worklog_host_id() -> str:
    env = (os.environ.get("WORKLOG_HOST_ID") or "").strip()
    if env:
        return env
    host_file = MEMORY_ROOT / ".env.host"
    if host_file.exists():
        for line in host_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("export WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
            if line.startswith("WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return ""


def _authority_host() -> str:
    env = (os.environ.get("WORKLOG_AUTHORITY_HOST") or "").strip()
    if env:
        return env
    marker = MEMORY_ROOT / "work-log" / "AUTHORITY_HOST"
    if marker.exists():
        for line in marker.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return "old-mac"


def assert_authority_or_exit(*, allow_non_authority: bool) -> None:
    if allow_non_authority:
        return
    host = _worklog_host_id() or "unknown"
    authority = _authority_host()
    if host != authority:
        print(
            f"skipped: host={host} is not authority={authority} "
            f"(daily DM push is old-mac only; use --allow-non-authority to override)",
            file=sys.stderr,
        )
        raise SystemExit(0)


def main() -> int:
    ap = argparse.ArgumentParser(description="Post daily report to TG bot private chat")
    ap.add_argument("--date", help="YYYY-MM-DD (default: Asia/Shanghai today)")
    ap.add_argument("--file", help="Explicit report markdown path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--allow-non-authority", action="store_true")
    args = ap.parse_args()

    if not args.dry_run:
        assert_authority_or_exit(allow_non_authority=args.allow_non_authority)

    token, users = _tg_creds()
    day = args.date or _today()
    if not users:
        print("ERROR: ALLOWED_USERS empty", file=sys.stderr)
        return 2

    try:
        path = resolve_report(day, args.file)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    body = path.read_text(encoding="utf-8")
    if not body.strip():
        print(f"ERROR: empty report: {path}", file=sys.stderr)
        return 1

    if already_posted(day) and not args.force and not args.dry_run:
        print(f"skipped: already posted for {day} (use --force to repost)")
        return 0

    payload = build_payload(day, body)
    parts = split_for_telegram(payload)

    if args.dry_run:
        print(
            f"=== DRY-RUN day={day} host={_worklog_host_id() or 'unknown'} "
            f"authority={_authority_host()} file={path} chats={users} parts={len(parts)} ==="
        )
        for i, part in enumerate(parts, 1):
            print(f"--- part {i}/{len(parts)} ({len(part)} chars) ---")
            print(part)
        return 0

    if not token:
        print(f"ERROR: TG_BOT_TOKEN empty (looked in {TGBOT_DIR}/.env)", file=sys.stderr)
        return 2

    sent_chats: list[int] = []
    for uid in users:
        for i, part in enumerate(parts):
            try:
                send_text(token, uid, part)
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", errors="replace")
                print(f"ERROR: send to {uid} part {i+1} failed: {e.code} {err}", file=sys.stderr)
                return 1
            except Exception as e:  # noqa: BLE001
                print(f"ERROR: send to {uid} part {i+1} failed: {e}", file=sys.stderr)
                return 1
        sent_chats.append(uid)
        print(f"posted to chat_id={uid} parts={len(parts)}")

    mark_posted(day, chat_ids=sent_chats, path=str(path))
    print(f"OK day={day} file={path} host={_worklog_host_id() or 'unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
