#!/usr/bin/env python3
"""双 Mac work-log 汇总：本机流水 → memory/hosts → 合并日文件 → 供统一日报。

用法：
  python3 worklog_dual_mac_sync.py              # 导出今日 + 合并
  python3 worklog_dual_mac_sync.py --date 2026-07-22
  python3 worklog_dual_mac_sync.py --all-local   # 导出本地 work-log 近 N 天

环境：
  MEMORY_DIR          默认 ~/.dc-platform/memory
  CHCODE_WORKLOG      默认 ~/Desktop/CHcode/.cursor/work-log
  WORKLOG_HOST_ID     默认 hostname -s（两机务必不同；可手动指定 new-mac / old-mac）
"""
from __future__ import annotations

import argparse
import os
import re
import socket
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))


def _host_id() -> str:
    raw = (os.environ.get("WORKLOG_HOST_ID") or "").strip()
    if raw:
        return re.sub(r"[^\w.\-]+", "-", raw)[:64]
    return re.sub(r"[^\w.\-]+", "-", socket.gethostname().split(".")[0])[:64] or "unknown-host"


def _paths() -> tuple[Path, Path]:
    mem = Path(os.environ.get("MEMORY_DIR") or Path.home() / ".dc-platform" / "memory")
    local = Path(
        os.environ.get("CHCODE_WORKLOG")
        or Path.home() / "Desktop" / "CHcode" / ".cursor" / "work-log"
    )
    return mem, local


def _today() -> str:
    return datetime.now(TZ).date().isoformat()


def _ensure_layout(mem_wl: Path) -> None:
    (mem_wl / "hosts").mkdir(parents=True, exist_ok=True)
    (mem_wl / "reports").mkdir(parents=True, exist_ok=True)


def _read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace").strip()


def export_host_day(mem_wl: Path, local_wl: Path, day: str, host: str) -> Path | None:
    """把本机当日流水/日报副本写到 hosts/<host>/。"""
    host_dir = mem_wl / "hosts" / host
    host_dir.mkdir(parents=True, exist_ok=True)
    (host_dir / "reports").mkdir(parents=True, exist_ok=True)

    day_src = local_wl / f"{day}.md"
    report_src = local_wl / "reports" / f"{day}-日报.md"
    wrote = False

    day_dst = host_dir / f"{day}.md"
    chunks: list[str] = [
        f"# work-log · {day} · host=`{host}`",
        f"> 导出时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %z')}",
        "",
    ]
    body = _read_text(day_src)
    if body:
        chunks.append("## 本机日流水")
        chunks.append("")
        chunks.append(body)
        chunks.append("")
        wrote = True
    report_body = _read_text(report_src)
    if report_body:
        chunks.append("## 本机日报稿")
        chunks.append("")
        chunks.append(report_body)
        chunks.append("")
        wrote = True
        (host_dir / "reports" / f"{day}-日报.md").write_text(
            report_body + "\n", encoding="utf-8"
        )

    if not wrote:
        return None
    day_dst.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return day_dst


def _iter_host_day_files(mem_wl: Path, day: str) -> list[tuple[str, Path]]:
    hosts = mem_wl / "hosts"
    if not hosts.exists():
        return []
    out: list[tuple[str, Path]] = []
    for d in sorted(hosts.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        p = d / f"{day}.md"
        if p.exists():
            out.append((d.name, p))
    return out


def merge_day(mem_wl: Path, day: str) -> Path:
    """合并各 host 当日流水 → work-log/YYYY-MM-DD.md（权威合并稿）。"""
    parts: list[str] = [
        f"# work-log · {day}（双机合并）",
        "",
        f"> 合并时间: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %z')}",
        "> 来源: `work-log/hosts/<host>/{day}.md`；正式日报见 `work-log/reports/{day}-日报.md`",
        "",
        "## 主机贡献",
        "",
    ]
    host_files = _iter_host_day_files(mem_wl, day)
    if not host_files:
        parts.append("_暂无各机流水（请先在本机写 `.cursor/work-log/` 再跑本脚本）_")
        parts.append("")
    else:
        for host, path in host_files:
            parts.append(f"- `{host}` ← `{path.relative_to(mem_wl.parent)}`")
        parts.append("")
        for host, path in host_files:
            parts.append(f"## host: {host}")
            parts.append("")
            parts.append(_read_text(path) or "_空_")
            parts.append("")

    # 附：各机已交日报稿路径提示
    report_hosts = []
    for host, _ in host_files:
        rp = mem_wl / "hosts" / host / "reports" / f"{day}-日报.md"
        if rp.exists():
            report_hosts.append(host)
    if report_hosts:
        parts.append("## 各机日报稿")
        parts.append("")
        for h in report_hosts:
            parts.append(f"- `hosts/{h}/reports/{day}-日报.md`")
        parts.append("")

    dst = mem_wl / f"{day}.md"
    dst.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    return dst


def _authority_host(mem_wl: Path) -> str:
    """正式日报权威主机：默认 old-mac（主人 2026-07-22 钦定）。"""
    env = (os.environ.get("WORKLOG_AUTHORITY_HOST") or "").strip()
    if env:
        return re.sub(r"[^\w.\-]+", "-", env)[:64]
    marker = mem_wl / "AUTHORITY_HOST"
    if marker.exists():
        for line in marker.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return re.sub(r"[^\w.\-]+", "-", line)[:64]
    return "old-mac"


def publish_canonical_report(mem_wl: Path, local_wl: Path, day: str, host: str) -> Path | None:
    """正式日报权威：以 AUTHORITY_HOST（默认 old-mac）为准。

    - 权威机：可用本机日报覆盖 `work-log/reports/`
    - 非权威机：只写到 `hosts/<自己>/reports/`，不覆盖权威稿；若权威稿已存在则镜像回本机
    """
    authority = _authority_host(mem_wl)
    local_report = local_wl / "reports" / f"{day}-日报.md"
    host_report = mem_wl / "hosts" / host / "reports" / f"{day}-日报.md"
    auth_report = mem_wl / "hosts" / authority / "reports" / f"{day}-日报.md"
    canon = mem_wl / "reports" / f"{day}-日报.md"
    local_wl.joinpath("reports").mkdir(parents=True, exist_ok=True)

    def _stamp(body: str, src_host: str) -> str:
        if "双机汇总" in body[:500] and "权威" in body[:500]:
            return body if body.endswith("\n") else body + "\n"
        lines = body.splitlines()
        insert_at = 0
        for i, line in enumerate(lines[:25]):
            if line.startswith("> 日期:") or line.startswith("> 日期："):
                insert_at = i + 1
                break
        notes = [
            f"> 双机汇总: 见 `~/.dc-platform/memory/work-log/{day}.md`（hosts 合并）",
            f"> 日报权威主机: `{src_host}`（非权威机不得覆盖正式稿）",
        ]
        for n in reversed(notes):
            if n not in lines[:30]:
                lines.insert(insert_at, n)
        return "\n".join(lines).rstrip() + "\n"

    # 1) 权威机：本机稿 → hosts/authority + reports 权威
    if host == authority:
        src = local_report if local_report.exists() else host_report
        if not src.exists():
            print(f"canonical: authority host `{authority}` 本日无本地日报稿")
            return canon if canon.exists() else None
        body = _stamp(_read_text(src), authority)
        if not body.strip():
            return None
        (mem_wl / "hosts" / authority / "reports").mkdir(parents=True, exist_ok=True)
        (mem_wl / "hosts" / authority / "reports" / f"{day}-日报.md").write_text(body, encoding="utf-8")
        canon.write_text(body, encoding="utf-8")
        local_report.write_text(body, encoding="utf-8")
        print(f"canonical: published by authority `{authority}`")
        return canon

    # 2) 非权威机：只归档自己的 hosts 稿，不覆盖 reports/
    if local_report.exists():
        body = _read_text(local_report)
        if body.strip():
            (mem_wl / "hosts" / host / "reports").mkdir(parents=True, exist_ok=True)
            host_report.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
            print(f"canonical: non-authority `{host}` archived to hosts only (not overwriting)")

    # 3) 若权威稿已在仓里，镜像到本机，保证新机读到旧机标准
    preferred = None
    if auth_report.exists():
        preferred = auth_report
    elif canon.exists():
        # 仅当权威机尚未上传 hosts 稿、但 reports 已有时沿用；若来自非权威则仍可被权威覆盖
        preferred = canon
    if preferred and preferred.exists():
        body = _read_text(preferred)
        if body.strip():
            local_report.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
            if preferred == auth_report:
                canon.write_text(_stamp(body, authority), encoding="utf-8")
            print(f"canonical: mirrored authority draft → local ({preferred.name})")
            return canon

    print(f"canonical: waiting for authority `{authority}` report")
    return None

def export_recent_local(mem_wl: Path, local_wl: Path, host: str, days: int) -> int:
    n = 0
    today = datetime.now(TZ).date()
    for i in range(days):
        day = (today - timedelta(days=i)).isoformat()
        if export_host_day(mem_wl, local_wl, day, host):
            merge_day(mem_wl, day)
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Dual-Mac work-log export + merge")
    ap.add_argument("--date", help="YYYY-MM-DD（默认今天 Asia/Shanghai）")
    ap.add_argument("--all-local", action="store_true", help="导出本地近 14 天有内容的流水")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--no-publish-report", action="store_true")
    args = ap.parse_args()

    mem, local = _paths()
    mem_wl = mem / "work-log"
    _ensure_layout(mem_wl)
    host = _host_id()
    day = args.date or _today()

    print(f"host={host}")
    print(f"memory_worklog={mem_wl}")
    print(f"local_worklog={local}")

    if args.all_local:
        n = export_recent_local(mem_wl, local, host, args.days)
        print(f"exported+merged days≈{n}")
    else:
        out = export_host_day(mem_wl, local, day, host)
        print(f"export: {out or '(no local day/report)'}")
        merged = merge_day(mem_wl, day)
        print(f"merged: {merged}")

    if not args.no_publish_report:
        pub = publish_canonical_report(mem_wl, local, day, host)
        print(f"canonical_report: {pub or '(none)'}")

    print("next: bash ~/.dc-platform/scripts/sync-memory-git.sh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
