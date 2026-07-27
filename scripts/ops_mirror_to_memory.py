#!/usr/bin/env python3
"""把本机「任务 / 所作所为」摘要镜像进 memory，供双 Mac Git 同步。

不同步：TG 聊天原文、tgbot.db、.env、Telethon session。
同步：近期 bus/派单溯源、未结案 bus、本机 host 当日 ops 摘要。

用法：
  python3 ops_mirror_to_memory.py
  python3 ops_mirror_to_memory.py --days 3

由 sync-memory-git.sh 每 10 分钟自动调用。
旧 Mac（bot 主控）会写 ops-mirror/LATEST.md；新 Mac 只写 hosts/<id>/。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=8))
BUS_SOURCES = frozenset({"agent_bus_in", "agent_bus_out", "worker_ant_group"})


def _host_id() -> str:
    raw = (os.environ.get("WORKLOG_HOST_ID") or "").strip()
    if raw:
        return re.sub(r"[^\w.\-]+", "-", raw)[:64]
    return re.sub(r"[^\w.\-]+", "-", socket.gethostname().split(".")[0])[:64] or "unknown-host"


def _mem() -> Path:
    return Path(os.environ.get("MEMORY_DIR") or Path.home() / ".dc-platform" / "memory")


def _chcode() -> Path:
    return Path(os.environ.get("CHCODE_ROOT") or Path.home() / "Desktop" / "CHcode")


def _today() -> str:
    return datetime.now(TZ).date().isoformat()


def _authority_host(mem: Path) -> str:
    p = mem / "work-log" / "AUTHORITY_HOST"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            return s
    return "old-mac"


def _load_provenance(days: int) -> list[dict]:
    path = _chcode() / "omdb" / "tgbot" / "data" / "task_provenance.jsonl"
    if not path.is_file():
        return []
    cutoff = (datetime.now(TZ).date() - timedelta(days=max(0, days - 1))).isoformat()
    out: list[dict] = []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = str(o.get("ts") or "")[:10]
            if ts and ts < cutoff:
                continue
            src = str(o.get("source") or "")
            if src not in BUS_SOURCES and not str(o.get("label") or "").startswith("bus"):
                # 私聊任务也算「所作所为」，但只留短标题
                if src != "telegram_dm":
                    continue
            out.append(o)
    return out[-80:]


def _open_bus_markdown() -> str:
    script = _chcode() / ".claude" / "database" / "scripts" / "notify" / "agent_bus_open.py"
    if not script.is_file():
        return ""
    env = os.environ.copy()
    env.setdefault(
        "AGENT_BUS_STATE_DIR",
        str(Path.home() / "Library" / "Application Support" / "youchu-agent-bus" / "state"),
    )
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--markdown"],
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
            cwd=str(script.parent),
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if r.returncode != 0:
        return ""
    return (r.stdout or "").strip()


def _fmt_prov(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_本日近窗无 bus/私聊任务溯源（或本机无 tgbot data）_"]
    lines = [
        "| 时间 | 标签 | 来源 | 状态 | 摘要 |",
        "|---|---|---|---|---|",
    ]
    for o in rows:
        ts = str(o.get("ts") or "")[:16]
        label = str(o.get("label") or "-")
        src = str(o.get("source") or "-")
        status = str(o.get("status") or "-")
        text = re.sub(r"\s+", " ", str(o.get("text") or ""))[:80]
        meta = o.get("meta") if isinstance(o.get("meta"), dict) else {}
        bus = meta.get("bus_id")
        if bus:
            label = f"{label} (bus#{bus})"
        lines.append(f"| {ts} | {label} | {src} | {status} | {text} |")
    return lines


def write_mirror(*, days: int = 2) -> Path:
    mem = _mem()
    host = _host_id()
    day = _today()
    root = mem / "ops-mirror"
    host_dir = root / "hosts" / host
    host_dir.mkdir(parents=True, exist_ok=True)

    prov = _load_provenance(days)
    open_md = _open_bus_markdown()
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %z")

    parts = [
        f"# ops-mirror · {day} · host=`{host}`",
        f"> 导出时间: {now}",
        f"> 说明: 任务/所作所为摘要；**不含** TG 聊天原文 / db / 密钥",
        "",
        "## 近期任务溯源（bus + 相关私聊）",
        "",
        *_fmt_prov(prov),
        "",
    ]
    if open_md:
        parts.extend(["## 未结案 agent-bus（本机实时）", "", open_md, ""])
    else:
        parts.extend(
            [
                "## 未结案 agent-bus（本机实时）",
                "",
                "_本机无 agent-bus state 或扫描失败（新 Mac 正常；以旧 Mac LATEST 为准）_",
                "",
            ]
        )

    host_day = host_dir / f"{day}.md"
    host_day.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")

    # 权威机写 LATEST，供新 Mac 直接读
    if host == _authority_host(mem):
        latest = [
            f"# ops-mirror · LATEST（权威机 `{host}`）",
            f"> 更新: {now}",
            "",
            f"详见当日: `ops-mirror/hosts/{host}/{day}.md`",
            "",
            "## 未结案 agent-bus",
            "",
            open_md or "_无未结案 / 本机未扫到_",
            "",
            "## 近期任务溯源（摘录）",
            "",
            *_fmt_prov(prov[-30:]),
            "",
        ]
        (root / "LATEST.md").write_text("\n".join(latest).rstrip() + "\n", encoding="utf-8")

    # 日合并：拼各 host
    merge = [
        f"# ops-mirror · {day}（双机）",
        f"> 合并时间: {now}",
        "",
    ]
    hosts_root = root / "hosts"
    if hosts_root.is_dir():
        for d in sorted(hosts_root.iterdir()):
            if not d.is_dir():
                continue
            p = d / f"{day}.md"
            if not p.exists():
                continue
            merge.append(f"## host `{d.name}`")
            merge.append("")
            merge.append(p.read_text(encoding="utf-8", errors="replace").strip())
            merge.append("")
    (root / f"{day}.md").write_text("\n".join(merge).rstrip() + "\n", encoding="utf-8")
    return host_day


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2)
    args = ap.parse_args()
    out = write_mirror(days=args.days)
    print(f"ops-mirror: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
