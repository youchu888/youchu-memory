#!/usr/bin/env python3
"""把「非代码」工作产物镜像进 youchu-memory，供双机同步。

同步（镜像）：
  - CHcode 核查报告 / playbook（.claude 与 .Codex）
  - Cursor agent-transcripts（按机分目录，近 N 天）
  - tgbot outgoing 文稿（不含 session / .env / db）

不同步（刻意）：
  - 业务代码仓正文、密钥、Telethon session、agent-bus 全量 state、VPN

agent-bus 只读对照副本另见 export_agent_bus_readonly_mirror.py（权威机导出 inbox/sent/processed）。
"""

from __future__ import annotations

import os
import re
import shutil
import time
from pathlib import Path

# 镜像进私人仓前脱敏（防 transcript 把口令又写回来）
# 已知泄露串只读本机 ~/.dc-platform/config/redact-known-secrets.local（不进 Git）
_REDACT = "***REDACTED***"
_KNOWN_SECRETS_FILE = Path.home() / ".dc-platform" / "config" / "redact-known-secrets.local"
_ASSIGN_RE = re.compile(
    r"(?i)(\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|bot[_-]?token|auth[_-]?token)\b\s*[=:]\s*)(['\"]?)([^'\"\s#,;]{4,})(\2)"
)
_ALLOW_VAL = re.compile(
    r"(?i)^(your-password|your_password|changeme|placeholder|\*+|x{3,}|TODO(_PASSWORD)?|None|null|true|false|"
    r"\$\{[^}]+\}|<[^>]+>|PASSWORD|password|passwd|secret|token|REDACTED|\*\*\*REDACTED\*\*\*|"
    r"os\.environ|getenv|getpass|process\.env|[A-Z][A-Z0-9_]{2,})$"
)
_CN_PWD_RE = re.compile(r"(密码[：:]\s*)([A-Za-z0-9@!#._\-]{4,})")


def _load_known_secrets() -> list[str]:
    if not _KNOWN_SECRETS_FILE.is_file():
        return []
    out: list[str] = []
    for line in _KNOWN_SECRETS_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out

HOME = Path.home()
MEM = Path(os.environ.get("MEMORY_GIT_DIR", HOME / ".dc-platform" / "memory"))
HOST = (os.environ.get("WORKLOG_HOST_ID") or "unknown-host").strip() or "unknown-host"

def _detect_chcode() -> Path:
    env = os.environ.get("CHCODE_ROOT", "").strip()
    if env:
        return Path(env)
    for cand in (
        HOME / "Desktop" / "CHcode",
        HOME / "Program" / "datacenter" / "dc-parent",
        Path("/Users/arthur/Program/datacenter/dc-parent"),
        Path("/Users/mac/Desktop/CHcode"),
    ):
        if (cand / ".claude" / "database").is_dir() or (cand / "ops_system").is_dir():
            return cand
    return HOME / "Desktop" / "CHcode"


# 默认工作仓（双机路径可能不同）
CHCODE = _detect_chcode()
TRANSCRIPTS = Path(
    os.environ.get(
        "CURSOR_TRANSCRIPTS_DIR",
        HOME
        / ".cursor"
        / "projects"
        / "Users-mac-Desktop-CHcode"
        / "agent-transcripts",
    )
)
TGBOT_OUT = CHCODE / "omdb" / "tgbot" / "outgoing"

# 近多少天的 transcript（按 mtime）
TRANSCRIPT_DAYS = int(os.environ.get("MIRROR_TRANSCRIPT_DAYS", "21"))
# 单文件上限（MB），超大跳过
MAX_FILE_MB = float(os.environ.get("MIRROR_MAX_FILE_MB", "8"))


def _load_host() -> str:
    envf = MEM / ".env.host"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("export WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
            if line.startswith("WORKLOG_HOST_ID="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return HOST


def _redact_text(text: str) -> str:
    for k in sorted(_load_known_secrets(), key=len, reverse=True):
        if k in text:
            text = text.replace(k, _REDACT)

    def _repl(m: re.Match[str]) -> str:
        val = m.group(3)
        if _ALLOW_VAL.match(val) or val.startswith("***"):
            return m.group(0)
        return f"{m.group(1)}{m.group(2)}{_REDACT}{m.group(4)}"

    text = _ASSIGN_RE.sub(_repl, text)
    text = _CN_PWD_RE.sub(lambda m: m.group(1) + _REDACT, text)
    return text


def _redact_file(path: Path) -> None:
    if path.suffix.lower() not in {".jsonl", ".json", ".md", ".txt", ".html", ".csv", ".yml", ".yaml", ".log"}:
        return
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    new = _redact_text(raw)
    if new != raw:
        path.write_text(new, encoding="utf-8")


def _copy_file(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    try:
        size_mb = src.stat().st_size / (1024 * 1024)
        if size_mb > MAX_FILE_MB:
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            sstat, dstat = src.stat(), dst.stat()
            if sstat.st_mtime <= dstat.st_mtime and sstat.st_size == dstat.st_size:
                return False
        shutil.copy2(src, dst)
        _redact_file(dst)
        return True
    except OSError:
        return False


def _mirror_tree(src_root: Path, dst_root: Path, *, exts: set[str] | None = None) -> int:
    if not src_root.is_dir():
        return 0
    n = 0
    for src in src_root.rglob("*"):
        if not src.is_file():
            continue
        if exts and src.suffix.lower() not in exts:
            continue
        # 跳过明显私货
        name = src.name.lower()
        if name.endswith((".env", ".session", ".pem", ".key")) or "credential" in name:
            continue
        rel = src.relative_to(src_root)
        if _copy_file(src, dst_root / rel):
            n += 1
    return n


def _mirror_transcripts(dst_root: Path, days: int) -> int:
    if not TRANSCRIPTS.is_dir():
        return 0
    cutoff = time.time() - days * 86400
    n = 0
    for src in TRANSCRIPTS.rglob("*.jsonl"):
        try:
            if src.stat().st_mtime < cutoff:
                continue
        except OSError:
            continue
        rel = src.relative_to(TRANSCRIPTS)
        if _copy_file(src, dst_root / rel):
            n += 1
    return n


def main() -> int:
    host = _load_host()
    root = MEM / "mirrors"
    root.mkdir(parents=True, exist_ok=True)

    stats: dict[str, int] = {}

    # 核查报告 / 剧本（非代码资产）
    for label, src in (
        ("datacheck-reports-claude", CHCODE / ".claude" / "database" / "reports"),
        ("datacheck-reports-codex", CHCODE / ".Codex" / "database" / "reports"),
        ("datacheck-playbooks-claude", CHCODE / ".claude" / "database" / "playbooks"),
        ("datacheck-playbooks-codex", CHCODE / ".Codex" / "database" / "playbooks"),
    ):
        stats[label] = _mirror_tree(src, root / label, exts={".md", ".html", ".json", ".csv", ".txt"})

    # 本机 transcript（按机隔离，减少双机同路径冲突）
    stats["agent-transcripts"] = _mirror_transcripts(
        root / "agent-transcripts" / host, TRANSCRIPT_DAYS
    )

    # tgbot 出站文稿（对接说明等）
    stats["tgbot-outgoing"] = _mirror_tree(
        TGBOT_OUT,
        root / "tgbot-outgoing" / host,
        exts={".md", ".html", ".json", ".csv", ".txt", ".xlsx"},
    )

    # 清单
    lines = [
        "# mirrors · 非代码双机镜像",
        "",
        f"- host: `{host}`",
        f"- updated: {time.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"- transcript_days: {TRANSCRIPT_DAYS}",
        "",
        "## 本轮复制文件数",
        "",
    ]
    for k, v in sorted(stats.items()):
        lines.append(f"- `{k}`: {v}")
    lines += [
        "",
        "## 范围",
        "",
        "| 同步 | 不同步 |",
        "|------|--------|",
        "| 核查报告 / playbook 副本、近窗 transcript、tgbot outgoing 文稿 | 业务代码、`.env`、session、agent-bus 全量 state、VPN |",
        "",
        "agent-bus 只读镜像见 `mirrors/agent-bus/`（`export_agent_bus_readonly_mirror.py`）。",
        "",
        "权威仍以各机写盘为准；本目录只做跨机可读备份。",
        "",
    ]
    (root / "README.md").write_text("\n".join(lines), encoding="utf-8")
    # 每机一份状态，避免双机抢写同一 README 冲突过大时仍有迹可查
    (root / f"LAST_EXPORT_{host}.md").write_text("\n".join(lines), encoding="utf-8")

    total = sum(stats.values())
    print(f"mirrors: host={host} copied={total} -> {root}")
    for k, v in sorted(stats.items()):
        if v:
            print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
