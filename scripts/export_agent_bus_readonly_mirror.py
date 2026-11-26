#!/usr/bin/env python3
"""agent-bus 只读镜像：权威机导出 → memory 仓 → 非权威机物化对照副本。

用途：人在 new-mac 写代码时对照派单 / 查历史，**不**在新机启 poller、不结案。

模式：
  export      仅 AUTHORITY_HOST 本机导出（可用 --force）
  materialize 非权威机把 mirrors/agent-bus/from-* 落到本机 readonly-mirror/
  both        先 export 再 materialize（给 sync-memory-git 用）

导出内容（脱敏后）：
  youchu_ai_inbox.jsonl / youchu_ai_sent.json / youchu_ai_processed.json /
  youchu_ai.offset / OPEN.md / MANIFEST.json

不同步：poller pid、wake_feed、锁文件、token、完整 tg_status 大日志。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from pathlib import Path

HOME = Path.home()
MEM = Path(os.environ.get("MEMORY_GIT_DIR", HOME / ".dc-platform" / "memory"))
STATE = Path(
    os.environ.get(
        "AGENT_BUS_STATE_DIR",
        str(HOME / "Library" / "Application Support" / "youchu-agent-bus" / "state"),
    )
)
MIRROR_ROOT = MEM / "mirrors" / "agent-bus"
LOCAL_READONLY = Path(
    os.environ.get(
        "AGENT_BUS_READONLY_DIR",
        str(HOME / "Library" / "Application Support" / "youchu-agent-bus" / "readonly-mirror"),
    )
)

EXPORT_FILES = (
    "youchu_ai_inbox.jsonl",
    "youchu_ai_sent.json",
    "youchu_ai_processed.json",
    "youchu_ai.offset",
)

_REDACT = "***REDACTED***"
_KNOWN = HOME / ".dc-platform" / "config" / "redact-known-secrets.local"
_ASSIGN_RE = re.compile(
    r"(?i)(\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|bot[_-]?token|auth[_-]?token)\b\s*[=:]\s*)(['\"]?)([^'\"\s#,;]{4,})(\2)"
)


def _load_host() -> str:
    envf = MEM / ".env.host"
    if envf.is_file():
        for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("export WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
            if line.startswith("WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return (os.environ.get("WORKLOG_HOST_ID") or "").strip() or "unknown-host"


def _authority_host() -> str:
    p = MEM / "work-log" / "AUTHORITY_HOST"
    if not p.is_file():
        return "old-mac"
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        return s
    return "old-mac"


def _redact(text: str) -> str:
    if _KNOWN.is_file():
        for k in sorted(
            (ln.strip() for ln in _KNOWN.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip() and not ln.strip().startswith("#")),
            key=len,
            reverse=True,
        ):
            if k in text:
                text = text.replace(k, _REDACT)
    return _ASSIGN_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}{_REDACT}{m.group(4)}", text)


def _copy_redacted(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    raw = src.read_bytes()
    # 文本类脱敏；offset 等小文件原样
    if src.suffix.lower() in {".json", ".jsonl", ".md", ".txt", ".log"} or src.name.endswith(".jsonl"):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dst)
            return True
        new = _redact(text)
        if dst.exists() and dst.read_text(encoding="utf-8", errors="ignore") == new:
            return False
        dst.write_text(new, encoding="utf-8")
        try:
            os.utime(dst, (src.stat().st_atime, src.stat().st_mtime))
        except OSError:
            pass
        return True
    if dst.exists() and dst.stat().st_size == src.stat().st_size and dst.stat().st_mtime >= src.stat().st_mtime:
        return False
    shutil.copy2(src, dst)
    return True


def _processed_ids(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    if isinstance(data, dict):
        return {str(k) for k in data.keys()}
    if isinstance(data, list):
        out: set[str] = set()
        for x in data:
            if isinstance(x, dict) and "id" in x:
                out.add(str(x["id"]))
            else:
                out.add(str(x))
        return out
    return set()


def _build_open_md(inbox: Path, processed: Path, *, limit: int = 80) -> str:
    done = _processed_ids(processed)
    opens: list[dict] = []
    if inbox.is_file():
        for line in inbox.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            bid = str(o.get("id") or "")
            if not bid or bid in done:
                continue
            opens.append(o)
    opens.sort(key=lambda x: int(x.get("id") or 0), reverse=True)
    lines = [
        "# agent-bus · 未结案（只读镜像）",
        "",
        f"- generated: {time.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"- open_count: {len(opens)}",
        f"- showing: {min(limit, len(opens))}",
        "",
        "| bus_id | from | created_at | 摘要 |",
        "|--------|------|------------|------|",
    ]
    for o in opens[:limit]:
        text = _redact(str(o.get("text") or "")).replace("|", "/").replace("\n", " ")
        if len(text) > 120:
            text = text[:117] + "..."
        lines.append(
            f"| {o.get('id')} | {o.get('from_agent','')} | {o.get('created_at','')} | {text} |"
        )
    lines.append("")
    lines.append("> 本文件只读对照。结案 / ack / reply 只在权威机（AUTHORITY_HOST）做。")
    lines.append("")
    return "\n".join(lines)


def do_export(*, force: bool = False) -> int:
    host = _load_host()
    auth = _authority_host()
    if not force and host != auth:
        print(f"agent-bus-mirror: skip export (host={host} authority={auth})")
        return 0
    if not STATE.is_dir():
        print(f"agent-bus-mirror: skip export (no state dir {STATE})")
        return 0
    dest = MIRROR_ROOT / f"from-{host}"
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for name in EXPORT_FILES:
        if _copy_redacted(STATE / name, dest / name):
            copied += 1
    open_md = _build_open_md(dest / "youchu_ai_inbox.jsonl", dest / "youchu_ai_processed.json")
    (dest / "OPEN.md").write_text(open_md, encoding="utf-8")
    manifest = {
        "host": host,
        "authority_host": auth,
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "state_dir": str(STATE),
        "files": list(EXPORT_FILES) + ["OPEN.md"],
        "copied": copied,
        "mode": "readonly-export",
        "note": "do-not-start-poller-on-consumer",
    }
    (dest / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    readme = MIRROR_ROOT / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# agent-bus 只读镜像",
                "",
                "权威机（`AUTHORITY_HOST`）导出 `from-<host>/`；其它机经 memory-git-sync 拉取后物化到",
                "`~/Library/Application Support/youchu-agent-bus/readonly-mirror/`。",
                "",
                "**禁止**在非权威机用这份副本启 poller / 写 processed / 当 inbox 真源。",
                "",
                f"- last_export_host: `{host}`",
                f"- authority: `{auth}`",
                f"- updated: {manifest['exported_at']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"agent-bus-mirror: export host={host} copied={copied} -> {dest}")
    return 0


def do_materialize() -> int:
    host = _load_host()
    auth = _authority_host()
    if host == auth:
        print(f"agent-bus-mirror: skip materialize (this host is authority={auth})")
        return 0
    src = MIRROR_ROOT / f"from-{auth}"
    if not src.is_dir():
        # 兼容：扫 from-* 取最新 MANIFEST
        cands = sorted(MIRROR_ROOT.glob("from-*"), key=lambda p: p.stat().st_mtime if p.is_dir() else 0, reverse=True)
        src = cands[0] if cands else src
    if not src.is_dir():
        print(f"agent-bus-mirror: skip materialize (no mirror yet under {MIRROR_ROOT})")
        return 0
    LOCAL_READONLY.mkdir(parents=True, exist_ok=True)
    n = 0
    for src_f in src.iterdir():
        if not src_f.is_file():
            continue
        dst = LOCAL_READONLY / src_f.name
        if src_f.suffix.lower() in {".json", ".jsonl", ".md", ".txt"} or src_f.name.endswith(".jsonl"):
            text = _redact(src_f.read_text(encoding="utf-8", errors="ignore"))
            if dst.exists() and dst.read_text(encoding="utf-8", errors="ignore") == text:
                continue
            dst.write_text(text, encoding="utf-8")
            n += 1
        else:
            shutil.copy2(src_f, dst)
            n += 1
    pointer = {
        "materialized_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "consumer_host": host,
        "source": str(src),
        "authority_host": auth,
        "readonly": True,
        "open_index": str(LOCAL_READONLY / "OPEN.md"),
    }
    (LOCAL_READONLY / "LOCAL_POINTER.json").write_text(
        json.dumps(pointer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (LOCAL_READONLY / "DO_NOT_START_POLLER").write_text(
        "This directory is a read-only mirror from the authority host.\n"
        "Do not point AGENT_BUS_STATE_DIR here. Do not start poller against these files.\n",
        encoding="utf-8",
    )
    print(f"agent-bus-mirror: materialize host={host} files={n} <- {src} -> {LOCAL_READONLY}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="agent-bus readonly mirror export/materialize")
    ap.add_argument(
        "mode",
        nargs="?",
        default="both",
        choices=("export", "materialize", "both"),
    )
    ap.add_argument("--force", action="store_true", help="非权威机也允许 export（排障）")
    args = ap.parse_args()
    rc = 0
    if args.mode in ("export", "both"):
        rc = do_export(force=args.force) or rc
    if args.mode in ("materialize", "both"):
        rc = do_materialize() or rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
