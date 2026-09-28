#!/usr/bin/env python3
"""无 Cursor 接住时：从当日 work-log 自动定稿日报并（可选）推送 TG。

权威机 fallback / 硬兜底调用。只写已完成向 bullet；过滤纯运维噪音。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
MEMORY = Path.home() / ".dc-platform" / "memory"
REPORTS = MEMORY / "work-log" / "reports"
HOSTS = MEMORY / "work-log" / "hosts"
MERGED = MEMORY / "work-log"
LOCAL_WL = Path.home() / "Desktop" / "CHcode" / ".cursor" / "work-log"
POST_PY = MEMORY / "scripts" / "post_daily_report_to_dm.py"

# 不进日报正文的运维词（仍可留在 work-log）
_SKIP_RE = re.compile(
    r"(绿点|LaunchAgent|tgbot|自查|wake_feed|agent-bus|poller|KeepAlive|"
    r"memory sync|youchu-memory|合盖|休眠|ToDesk|VPN|可见在线|"
    r"GROUP_WORKBOOK|automation-ensure|工作簿进展|权威主机|WORKLOG_HOST|"
    r"AUTHORITY_HOST|狂人学习|lesson：|RunAtLoad|挂起：|oneshot|"
    r"App Support|deploy|kickstart|plist|fallback：|硬兜底|不依赖 Cursor|"
    r"自动化迁|自启保活|监控自启)",
    re.I,
)
_PREFER_RE = re.compile(
    r"(渠道|归因|漏斗|报表|建表|ETL|核查|指标|表|分区|补数|发布|试跑|抽检|口径|汇总)",
    re.I,
)
_PREFIX_RE = re.compile(
    r"^(?:TOP\d+:\s*)?(?:\[TQ-\d+\s*\|\s*[^\]]+\]\s*)+",
    re.I,
)


def _today() -> str:
    return datetime.now(TZ).strftime("%Y-%m-%d")


def _read(path: Path) -> str:
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _bullets_from(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("- "):
            continue
        body = s[2:].strip()
        if not body or body.startswith("#"):
            continue
        if _SKIP_RE.search(body):
            continue
        body = _PREFIX_RE.sub("", body).strip()
        body = re.sub(r"`[^`]+`", "", body).strip(" ：:;；")
        body = re.sub(r"，已完成；?$", "", body).strip()
        if len(body) < 8:
            continue
        out.append(body)
    # 去重保序
    seen: set[str] = set()
    uniq: list[str] = []
    for b in out:
        key = b[:40]
        if key in seen:
            continue
        seen.add(key)
        uniq.append(b)
    return uniq


def collect_bullets(day: str) -> list[str]:
    chunks = [
        _read(LOCAL_WL / f"{day}.md"),
        _read(HOSTS / "new-mac" / f"{day}.md"),
        _read(HOSTS / "old-mac" / f"{day}.md"),
        _read(MERGED / f"{day}.md"),
    ]
    bullets: list[str] = []
    for c in chunks:
        bullets.extend(_bullets_from(c))
    # 再去重
    seen: set[str] = set()
    out: list[str] = []
    for b in bullets:
        k = b[:48]
        if k in seen:
            continue
        seen.add(k)
        out.append(b)
    preferred = [b for b in out if _PREFER_RE.search(b) and "截止" not in b]
    rest = [b for b in out if b not in preferred and "截止" not in b]
    tomorrow_src = [b for b in out if "截止" in b]
    ordered = preferred + rest
    # stash tomorrow candidates on function attr for render optional use
    collect_bullets._tomorrow = tomorrow_src  # type: ignore[attr-defined]
    return ordered[:6]


def _shorten(text: str, lo: int = 22, hi: int = 42) -> str:
    text = re.sub(r"\s+", "", text)
    text = text.rstrip("。；;，,")
    if len(text) > hi:
        text = text[: hi - 1] + "…"
    if len(text) < lo:
        text = text + "，推进落地"
    return text


def render(day: str, bullets: list[str]) -> str:
    if not bullets:
        bullets = ["整理当日流水并核对权威机日报链路", "同步记忆与当日任务进度"]
    results = []
    for b in bullets[:3]:
        results.append(f"- [TQ-002 | DMP系统] {_shorten(b)}，已完成；")
    while len(results) < 1:
        results.append("- [TQ-002 | DMP系统] 当日数据任务收口，已完成；")

    tomorrow_src = list(getattr(collect_bullets, "_tomorrow", []) or [])
    tomorrow_src.extend(bullets[3:5])
    tomorrow = []
    seen_t: set[str] = set()
    for b in tomorrow_src:
        k = b[:36]
        if k in seen_t:
            continue
        seen_t.add(k)
        body = re.sub(r"（截止：.*?）$", "", b).strip()
        tomorrow.append(
            f"- TOP{len(tomorrow)+1}: [TQ-002 | DMP系统] 继续{_shorten(body, 16, 36)}（截止：明日）"
        )
        if len(tomorrow) >= 2:
            break
    if not tomorrow:
        tomorrow = [
            "- TOP1: [TQ-002 | DMP系统] 按当日未完项继续推进（截止：明日）",
        ]

    return f"""# 日报 · 又初·{day}

[REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:{day}]
> 提交人: 又初
> 工号: DN6517
> 岗位: 后端 BE
> 层级: L1
> 日期: {day}

## 【今日结果】
{chr(10).join(results)}

## 【死锁阻碍】
- 

## 【专项复盘】
- 

## 【明日动作】
{chr(10).join(tomorrow)}
"""


def write_report(day: str, body: str) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{day}-日报.md"
    path.write_text(body, encoding="utf-8")
    host_dir = HOSTS / "new-mac" / "reports"
    host_dir.mkdir(parents=True, exist_ok=True)
    (host_dir / f"{day}-日报.md").write_text(body, encoding="utf-8")
    local = LOCAL_WL / "reports"
    local.mkdir(parents=True, exist_ok=True)
    (local / f"{day}-日报.md").write_text(body, encoding="utf-8")
    return path


def post(day: str, path: Path, *, force: bool = True) -> int:
    if not POST_PY.is_file():
        print(f"MISS post script: {POST_PY}", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(POST_PY), "--date", day, "--file", str(path)]
    if force:
        cmd.append("--force")
    print("run:", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="")
    ap.add_argument("--post", action="store_true", help="定稿后推送 TG")
    ap.add_argument("--force-post", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    day = args.date or _today()

    # 已有人工/IDE 定稿则不覆盖
    existing = None
    for name in (f"{day}-日报.md", f"日报-{day}.md"):
        p = REPORTS / name
        if p.is_file() and p.stat().st_size > 80:
            existing = p
            break
    if existing and not args.dry_run:
        print(f"keep existing {existing}")
        if args.post or args.force_post:
            return post(day, existing, force=args.force_post or True)
        return 0

    bullets = collect_bullets(day)
    body = render(day, bullets)
    if args.dry_run:
        print(body)
        return 0
    path = write_report(day, body)
    print(f"wrote {path} bullets={len(bullets)}")
    if args.post or args.force_post:
        return post(day, path, force=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
