#!/usr/bin/env python3
"""向 @center_dc_vpn_bot 发送 /request，拉取 .ovpn 并导入 OpenVPN Connect。

依赖：telethon、PySocks（与 omdb/tgbot 相同）
首次：在 omdb/tgbot/.env 配置 TELEGRAM_API_ID/HASH，运行 login_user_session.py

用法：
  python3 vpn_ovpn_sync.py              # 完整流程：请求 → 下载 → 导入 → 重连
  python3 vpn_ovpn_sync.py --dry-run    # 只请求并下载，不碰 OpenVPN
  python3 vpn_ovpn_sync.py --import-only /path/to/file.ovpn
  python3 vpn_ovpn_sync.py --watch-downloads          # 监听配置目录，手动 /request 保存后自动导入
  python3 vpn_ovpn_sync.py --watch-downloads --once   # 导入目录里最新一份后退出
  python3 vpn_ovpn_sync.py --check                    # 检查依赖与配置，不执行
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DC_HOME = Path(os.environ.get("DC_PLATFORM_HOME", Path.home() / ".dc-platform"))
VPN_DIR = DC_HOME / "vpn"
STATE_FILE = VPN_DIR / "last_sync.json"
LOG_FILE = VPN_DIR / "sync.log"
DEFAULT_OVPN_DIR = Path.home() / "Desktop/CH/auto_vpn"

DEFAULT_ENV = SCRIPT_DIR / "vpn_ovpn_sync.env"
TGBOT_ENV = Path.home() / "Desktop/CHcode/omdb/tgbot/.env"

OPENVPN_CLI = Path(
    "/Applications/OpenVPN Connect/OpenVPN Connect.app/Contents/MacOS/OpenVPN Connect"
)

VPN_BOT = "center_dc_vpn_bot"
VPN_REQUEST_CMD = "/request"
DOWNLOADS_GLOB = "center_dc*又初*.ovpn"
VPN_PROFILE_GLOB = re.compile(r"center_dc.*又初.*\.ovpn$", re.I)
PROFILE_NAME = "center_dc_又初"
KEEP_PROFILES = 2
REQUEST_TIMEOUT = 120
DEFAULT_WATCH_POLL_SEC = 8
# 近期已下载则跳过 /request（防 dry-run+全量 或误连点重复拉证）
DEFAULT_REUSE_OVPN_MINUTES = 60
# 距上次导入满 N 小时即提前续期（证书名义 24h，实际可宽限，默认提前 1h）
DEFAULT_RENEW_AFTER_HOURS = 23
# 解析 notAfter 仅作兜底（无 imported_at 记录时）
DEFAULT_CERT_RENEW_BEFORE_MINUTES = 60

log = logging.getLogger("vpn_ovpn_sync")


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def load_config() -> dict:
    for p in (
        Path(os.environ.get("VPN_OVPN_SYNC_ENV", DEFAULT_ENV)),
        TGBOT_ENV,
    ):
        _load_dotenv(p)

    api_id = int(os.environ.get("TELEGRAM_API_ID", "0") or "0")
    api_hash = os.environ.get("TELEGRAM_API_HASH", "").strip()
    session = os.environ.get(
        "USER_SESSION_PATH",
        str(Path.home() / "Desktop/CHcode/omdb/tgbot/data/user_telegram"),
    )
    proxy = os.environ.get("TG_PROXY_URL", "").strip() or None
    bot = os.environ.get("VPN_BOT", VPN_BOT).strip().lstrip("@")
    cmd = os.environ.get("VPN_REQUEST_CMD", VPN_REQUEST_CMD).strip()
    profile_name = os.environ.get("VPN_PROFILE_NAME", PROFILE_NAME).strip()
    cli = Path(os.environ.get("OPENVPN_CLI", str(OPENVPN_CLI)))
    ovpn_dir = Path(
        os.environ.get("VPN_OVPN_DIR", str(DEFAULT_OVPN_DIR))
    ).expanduser()
    downloads_dir = Path(
        os.environ.get("VPN_DOWNLOADS_DIR", str(ovpn_dir))
    ).expanduser()
    keep_profiles = int(os.environ.get("VPN_KEEP_PROFILES", str(KEEP_PROFILES)) or KEEP_PROFILES)
    watch_poll = int(os.environ.get("VPN_WATCH_POLL_SEC", str(DEFAULT_WATCH_POLL_SEC)) or DEFAULT_WATCH_POLL_SEC)
    reuse_minutes = int(
        os.environ.get("VPN_REUSE_OVPN_MINUTES", str(DEFAULT_REUSE_OVPN_MINUTES))
        or DEFAULT_REUSE_OVPN_MINUTES
    )
    renew_before = int(
        os.environ.get(
            "VPN_CERT_RENEW_BEFORE_MINUTES",
            str(DEFAULT_CERT_RENEW_BEFORE_MINUTES),
        )
        or DEFAULT_CERT_RENEW_BEFORE_MINUTES
    )
    renew_after_hours = float(
        os.environ.get("VPN_RENEW_AFTER_HOURS", str(DEFAULT_RENEW_AFTER_HOURS))
        or DEFAULT_RENEW_AFTER_HOURS
    )

    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "session": session,
        "proxy": proxy,
        "bot": bot,
        "cmd": cmd,
        "profile_name": profile_name,
        "openvpn_cli": cli,
        "ovpn_dir": ovpn_dir,
        "downloads_dir": downloads_dir,
        "keep_profiles": keep_profiles,
        "watch_poll_sec": watch_poll,
        "reuse_ovpn_minutes": max(0, reuse_minutes),
        "cert_renew_before_minutes": max(0, renew_before),
        "renew_after_hours": max(0.5, renew_after_hours),
    }


def setup_logging() -> None:
    VPN_DIR.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(VPN_DIR, 0o700)
    except OSError:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def session_ready(session_path: str) -> bool:
    p = Path(session_path)
    return p.with_suffix(".session").exists() or p.exists()


def load_state() -> dict:
    if not STATE_FILE.is_file():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def file_fingerprint(path: Path) -> dict:
    st = path.stat()
    return {"path": str(path.resolve()), "mtime": int(st.st_mtime), "size": st.st_size}


def already_imported(path: Path, state: dict) -> bool:
    last = state.get("last_import") or {}
    fp = file_fingerprint(path)
    return (
        last.get("path") == fp["path"]
        and last.get("mtime") == fp["mtime"]
        and last.get("size") == fp["size"]
    )


def parse_iso_dt(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def get_imported_at(state: dict, ovpn_path: Path | None = None) -> datetime | None:
    """上次成功导入时间（UTC），优先 state.imported_at。"""
    for key in ("imported_at", "ts"):
        raw = state.get(key)
        if raw:
            dt = parse_iso_dt(str(raw))
            if dt is not None:
                return dt.astimezone(timezone.utc)
    if ovpn_path and ovpn_path.is_file():
        return datetime.fromtimestamp(ovpn_path.stat().st_mtime, tz=timezone.utc)
    return None


def import_needs_renewal(
    state: dict,
    *,
    renew_after_hours: float,
    ovpn_path: Path | None = None,
) -> bool:
    """按导入时刻 + 滚动小时数判断是否需要续期。"""
    imported = get_imported_at(state, ovpn_path)
    if imported is None:
        log.warning("无导入时间记录，将尝试续期")
        return True
    age_hours = (datetime.now(timezone.utc) - imported).total_seconds() / 3600.0
    if age_hours >= renew_after_hours:
        log.info(
            "距上次导入 %.1f 小时（阈值 %.1fh，导入于 %s UTC），需要续期",
            age_hours,
            renew_after_hours,
            imported.strftime("%Y-%m-%d %H:%M:%S"),
        )
        return True
    return False


def next_renew_at(state: dict, *, renew_after_hours: float, ovpn_path: Path | None = None) -> datetime | None:
    imported = get_imported_at(state, ovpn_path)
    if imported is None:
        return None
    return imported + timedelta(hours=renew_after_hours)


def parse_ovpn_cert_expiry(path: Path) -> datetime | None:
    """解析 .ovpn 内 <cert> 块的 notAfter（UTC）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(
        r"<cert>\s*(-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----)\s*</cert>",
        text,
        re.DOTALL,
    )
    if not m:
        return None
    cert_pem = m.group(1)
    tmp = tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False)
    try:
        tmp.write(cert_pem)
        tmp.close()
        proc = subprocess.run(
            ["openssl", "x509", "-in", tmp.name, "-noout", "-enddate"],
            capture_output=True,
            text=True,
            check=True,
        )
        date_str = proc.stdout.strip().split("=", 1)[1]
        return datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(
            tzinfo=timezone.utc
        )
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
    finally:
        Path(tmp.name).unlink(missing_ok=True)


def cert_needs_renewal(path: Path, *, within_minutes: int) -> bool:
    """兜底：无 imported_at 时用证书 notAfter（名义到期，实际可宽限）。"""
    expiry = parse_ovpn_cert_expiry(path)
    if expiry is None:
        log.warning("无法解析证书到期时间: %s，将尝试续期", path.name)
        return True
    now = datetime.now(timezone.utc)
    threshold = now + timedelta(minutes=within_minutes)
    if expiry <= now:
        log.info("证书已过期: %s（到期 %s UTC）", path.name, expiry.isoformat())
        return True
    if expiry <= threshold:
        log.info(
            "证书即将过期: %s（到期 %s UTC，<%d 分钟）",
            path.name,
            expiry.isoformat(),
            within_minutes,
        )
        return True
    return False


def ensure_ovpn_dir(cfg: dict) -> Path:
    d = cfg["ovpn_dir"]
    d.mkdir(parents=True, exist_ok=True)
    return d


def local_ovpn_path(cfg: dict) -> Path:
    return cfg["ovpn_dir"] / f"{cfg['profile_name']}.ovpn"


def archive_ovpn_copy(cfg: dict, latest: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive = cfg["ovpn_dir"] / f"{cfg['profile_name']}_{ts}.ovpn"
    shutil.copy2(latest, archive)
    log.info("存档 → %s", archive)
    return archive


def ovpn_age_minutes(path: Path) -> float:
    return max(0.0, (time.time() - path.stat().st_mtime) / 60.0)


def is_fresh_ovpn(path: Path, *, max_age_minutes: int) -> bool:
    return path.is_file() and path.stat().st_size > 0 and ovpn_age_minutes(path) <= max_age_minutes


async def obtain_ovpn(cfg: dict, *, force_request: bool = False) -> tuple[Path, bool]:
    """返回 (ovpn路径, 是否复用本地缓存未发 /request)。"""
    cached = local_ovpn_path(cfg)
    reuse_min = cfg["reuse_ovpn_minutes"]
    if not force_request and reuse_min > 0 and is_fresh_ovpn(cached, max_age_minutes=reuse_min):
        log.info(
            "复用本地配置 %s（%.0f 分钟前下载，<%d 分钟不再 /request）",
            cached,
            ovpn_age_minutes(cached),
            reuse_min,
        )
        return cached, True
    ovpn = await request_ovpn_from_bot(cfg)
    return ovpn, False


def _parse_proxy(url: str | None):
    if not url:
        return None
    try:
        import socks
    except ImportError:
        log.warning("未安装 PySocks，忽略 TG_PROXY_URL")
        return None
    from urllib.parse import urlparse

    u = urlparse(url)
    scheme = (u.scheme or "socks5").lower()
    host = u.hostname or "127.0.0.1"
    port = u.port or (1080 if scheme.startswith("socks") else 8080)
    mapping = {"socks5": socks.SOCKS5, "socks4": socks.SOCKS4, "http": socks.HTTP}
    return (mapping.get(scheme, socks.SOCKS5), host, port)


def _client_kwargs(proxy: str | None) -> dict:
    kw: dict = {}
    p = _parse_proxy(proxy)
    if p:
        kw["proxy"] = p
    return kw


def check_prerequisites(cfg: dict, *, require_telethon: bool = True) -> list[str]:
    issues: list[str] = []
    ok: list[str] = []

    if cfg["openvpn_cli"].is_file():
        ok.append(f"OpenVPN CLI: {cfg['openvpn_cli']}")
    else:
        issues.append(f"OpenVPN Connect CLI 不存在: {cfg['openvpn_cli']}")

    if require_telethon:
        if cfg["api_id"] and cfg["api_hash"]:
            ok.append("Telegram API: 已配置")
        else:
            issues.append(
                "缺少 TELEGRAM_API_ID / TELEGRAM_API_HASH → 写入 "
                f"{TGBOT_ENV}"
            )
        if session_ready(cfg["session"]):
            ok.append(f"Telethon 会话: {cfg['session']}.session")
        else:
            issues.append(
                "Telethon 未登录 → cd ~/Desktop/CHcode/omdb/tgbot && "
                "python3 login_user_session.py"
            )
        try:
            import telethon  # noqa: F401
            ok.append("telethon: 已安装")
        except ImportError:
            issues.append("缺少 telethon → pip install telethon PySocks")

    if cfg["ovpn_dir"].is_dir():
        ok.append(f"配置目录: {cfg['ovpn_dir']}")
    else:
        issues.append(f"配置目录不存在: {cfg['ovpn_dir']}（将自动创建）")

    if cfg["downloads_dir"].is_dir():
        ok.append(f"监听目录: {cfg['downloads_dir']}")
    else:
        issues.append(f"监听目录不存在: {cfg['downloads_dir']}")

    for line in ok:
        log.info("✓ %s", line)
    for line in issues:
        log.error("✗ %s", line)
    return issues


async def request_ovpn_from_bot(cfg: dict) -> Path:
    if not cfg["api_id"] or not cfg["api_hash"]:
        raise RuntimeError("缺少 TELEGRAM_API_ID / TELEGRAM_API_HASH（见 tgbot/.env）")
    if not session_ready(cfg["session"]):
        raise RuntimeError(
            "Telethon 未登录。请先运行:\n"
            "  cd ~/Desktop/CHcode/omdb/tgbot && python3 login_user_session.py"
        )

    try:
        from telethon import TelegramClient
    except ImportError as exc:
        raise RuntimeError("请安装: pip install telethon PySocks") from exc

    dest = local_ovpn_path(cfg)
    ensure_ovpn_dir(cfg)
    client = TelegramClient(
        cfg["session"],
        cfg["api_id"],
        cfg["api_hash"],
        **_client_kwargs(cfg["proxy"]),
    )

    async with client:
        bot = await client.get_entity(cfg["bot"])
        log.info("向 @%s 发送 %s", cfg["bot"], cfg["cmd"])
        async with client.conversation(bot, timeout=REQUEST_TIMEOUT) as conv:
            await conv.send_message(cfg["cmd"])
            while True:
                msg = await conv.get_response()
                text = (msg.text or msg.message or "").strip()
                if msg.document:
                    fname = None
                    for attr in msg.document.attributes:
                        if hasattr(attr, "file_name") and attr.file_name:
                            fname = attr.file_name
                            break
                    if fname and not VPN_PROFILE_GLOB.search(fname):
                        log.warning("收到非预期文件名 %s，仍继续下载", fname)
                    await client.download_media(msg, file=str(dest))
                    log.info("已下载 → %s (%d bytes)", dest, dest.stat().st_size)
                    archive_ovpn_copy(cfg, dest)
                    return dest
                if text:
                    log.info("Bot: %s", text.replace("\n", " | "))
                    if any(x in text.lower() for x in ("失败", "错误", "error", "failed")):
                        raise RuntimeError(f"VPN Bot 返回错误: {text[:300]}")
                else:
                    log.debug("收到非文档非文字消息，继续等待…")

    raise RuntimeError("超时：未收到 .ovpn 文件")


def run_async_with_retry(factory, *, retries: int = 5, delay_sec: float = 6.0):
    """Telethon 与 tgbot 共用会话时可能 sqlite locked，短暂重试。"""
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return asyncio.run(factory())
        except Exception as exc:
            if "database is locked" not in str(exc).lower():
                raise
            last_exc = exc
            if attempt < retries:
                log.warning(
                    "Telethon 会话被占用，%ds 后重试 (%d/%d)",
                    int(delay_sec),
                    attempt,
                    retries,
                )
                time.sleep(delay_sec)
    assert last_exc is not None
    raise last_exc


def _run_cli(cli: Path, *args: str) -> subprocess.CompletedProcess:
    if not cli.is_file():
        raise RuntimeError(f"OpenVPN Connect CLI 不存在: {cli}")
    cmd = [str(cli), *args]
    log.info("执行: %s", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def quit_openvpn() -> None:
    subprocess.run(
        ["osascript", "-e", 'quit app "OpenVPN Connect"'],
        capture_output=True,
        timeout=15,
    )
    time.sleep(3)


def list_profiles(cli: Path) -> list[dict]:
    proc = _run_cli(cli, "--list-profiles")
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "list-profiles 失败")
    raw = (proc.stdout or "").strip()
    if not raw:
        return []
    data = json.loads(raw)
    return data if isinstance(data, list) else []


def remove_matching_profiles(cli: Path, profile_name: str) -> int:
    removed = 0
    for p in list_profiles(cli):
        if profile_name not in (p.get("name") or ""):
            continue
        pid = p.get("id")
        if not pid:
            continue
        log.info("删除 profile: %s (%s)", p.get("name"), pid)
        proc = _run_cli(cli, f"--remove-profile={pid}")
        if proc.returncode != 0:
            log.warning("删除失败 %s: %s", pid, (proc.stderr or proc.stdout)[:200])
        else:
            removed += 1
    return removed


def cleanup_old_profiles(cli: Path, profile_name: str, keep: int = KEEP_PROFILES) -> None:
    profiles = list_profiles(cli)
    matched = [p for p in profiles if profile_name in (p.get("name") or "")]
    if len(matched) <= keep:
        return
    matched.sort(key=lambda p: int(p.get("id") or 0))
    to_remove = matched[:-keep]
    for p in to_remove:
        pid = p.get("id")
        if not pid:
            continue
        log.info("删除旧 profile: %s (%s)", p.get("name"), pid)
        proc = _run_cli(cli, f"--remove-profile={pid}")
        if proc.returncode != 0:
            log.warning("删除失败 %s: %s", pid, (proc.stderr or proc.stdout)[:200])


def _import_result_ok(out: str) -> bool:
    raw = (out or "").strip()
    if not raw:
        return True
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return True
    if isinstance(data, dict) and data.get("status") == "error":
        return False
    return True


def import_profile(cli: Path, ovpn_path: Path, profile_name: str, *, keep: int = KEEP_PROFILES) -> None:
    quit_openvpn()
    remove_matching_profiles(cli, profile_name)
    proc = _run_cli(cli, f"--import-profile={ovpn_path}")
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or not _import_result_ok(out):
        raise RuntimeError(f"import-profile 失败: {out[:500]}")
    log.info("导入成功: %s", out[:300].strip())
    cleanup_old_profiles(cli, profile_name, keep=keep)


def ensure_connect_on_launch(cli: Path) -> None:
    proc = _run_cli(cli, "--set-setting=connect-on-launch", "--value=true")
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if proc.returncode != 0:
        log.warning("打开 connect-on-launch 失败: %s", out[:200])
    else:
        log.info("已确保 connect-on-launch=true")


def latest_profile_id(cli: Path, profile_name: str) -> str | None:
    matched = [p for p in list_profiles(cli) if profile_name in (p.get("name") or "")]
    if not matched:
        return None
    matched.sort(key=lambda p: int(p.get("id") or 0))
    pid = matched[-1].get("id")
    return str(pid) if pid else None


def relaunch_openvpn() -> None:
    """导入会先拉起客户端；必须退出再开，connect-on-launch 才会生效。"""
    cli = OPENVPN_CLI
    ensure_connect_on_launch(cli)
    pid = latest_profile_id(cli, PROFILE_NAME)
    quit_openvpn()
    cmd = ["open", "-a", "OpenVPN Connect"]
    if pid:
        cmd.extend(["--args", f"--connect-shortcut={pid}"])
        log.info("已启动 OpenVPN Connect，并指定连接 profile %s", pid)
    else:
        log.info("已启动 OpenVPN Connect（connect-on-launch）")
    subprocess.run(cmd, check=False, timeout=15)


def save_state(
    ovpn_path: Path,
    *,
    dry_run: bool = False,
    mode: str = "sync",
    record_import: bool = False,
) -> None:
    prev = load_state()
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "ovpn": str(ovpn_path),
        "dry_run": dry_run,
        "mode": mode,
        "last_import": file_fingerprint(ovpn_path),
    }
    if record_import and not dry_run:
        payload["imported_at"] = datetime.now(timezone.utc).isoformat()
    elif prev.get("imported_at"):
        payload["imported_at"] = prev["imported_at"]
    STATE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def find_latest_download(downloads_dir: Path) -> Path | None:
    candidates = [
        p
        for p in downloads_dir.glob(DOWNLOADS_GLOB)
        if p.is_file() and p.stat().st_size > 0
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def import_from_downloads(
    cfg: dict,
    *,
    relaunch: bool = True,
    force: bool = False,
) -> Path | None:
    ovpn = find_latest_download(cfg["downloads_dir"])
    if not ovpn:
        log.info("Downloads 中暂无匹配 %s", DOWNLOADS_GLOB)
        return None

    state = load_state()
    if not force and already_imported(ovpn, state):
        log.info("跳过已导入文件: %s", ovpn.name)
        return ovpn

    log.info("准备导入: %s", ovpn)
    import_profile(
        cfg["openvpn_cli"],
        ovpn,
        cfg["profile_name"],
        keep=cfg["keep_profiles"],
    )
    if relaunch:
        relaunch_openvpn()
    save_state(ovpn, mode="watch-downloads", record_import=True)
    return ovpn


def watch_downloads(cfg: dict, *, once: bool = False, relaunch: bool = True) -> int:
    poll = max(3, cfg["watch_poll_sec"])
    log.info(
        "监听 %s (%s)，轮询 %ds；手动 /request 保存后自动导入",
        cfg["downloads_dir"],
        DOWNLOADS_GLOB,
        poll,
    )
    if once:
        ovpn = import_from_downloads(cfg, relaunch=relaunch)
        if ovpn:
            log.info("✅ 已处理 %s", ovpn.name)
            return 0
        return 1

    while True:
        try:
            ovpn = import_from_downloads(cfg, relaunch=relaunch)
            if ovpn:
                log.info("✅ 已导入 %s", ovpn.name)
        except Exception as exc:
            log.error("导入失败: %s", exc)
        time.sleep(poll)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VPN 配置自动同步（center_dc_vpn_bot）")
    parser.add_argument("--dry-run", action="store_true", help="只请求下载，不导入 OpenVPN")
    parser.add_argument("--import-only", metavar="PATH", help="跳过 TG，直接导入指定 .ovpn")
    parser.add_argument("--no-relaunch", action="store_true", help="导入后不重启 OpenVPN Connect")
    parser.add_argument(
        "--watch-downloads",
        action="store_true",
        help="监听配置目录，手动 /request 保存 .ovpn 后自动导入（无需 Telethon API）",
    )
    parser.add_argument("--once", action="store_true", help="配合 --watch-downloads：处理最新一份后退出")
    parser.add_argument("--force", action="store_true", help="忽略已导入记录，强制重新导入")
    parser.add_argument(
        "--force-request",
        action="store_true",
        help="忽略近期本地缓存，强制向 Bot 发 /request",
    )
    parser.add_argument("--check", action="store_true", help="检查依赖与配置")
    args = parser.parse_args(argv)

    setup_logging()
    cfg = load_config()
    ensure_ovpn_dir(cfg)
    cli = cfg["openvpn_cli"]
    relaunch = not args.no_relaunch

    if args.check:
        issues = check_prerequisites(
            cfg,
            require_telethon=not args.watch_downloads,
        )
        return 0 if not issues else 1

    try:
        if args.watch_downloads:
            issues = check_prerequisites(cfg, require_telethon=False)
            if issues:
                raise RuntimeError("前置检查未通过，见上方 ✗")
            return watch_downloads(cfg, once=args.once, relaunch=relaunch)

        if args.import_only:
            ovpn = Path(args.import_only).expanduser().resolve()
            if not ovpn.is_file():
                raise RuntimeError(f"文件不存在: {ovpn}")
            import_profile(cli, ovpn, cfg["profile_name"], keep=cfg["keep_profiles"])
            if relaunch:
                relaunch_openvpn()
            save_state(ovpn, mode="import-only", record_import=True)
        else:
            issues = check_prerequisites(cfg, require_telethon=True)
            if issues:
                raise RuntimeError("前置检查未通过，见上方 ✗")

            state = load_state()
            cached = local_ovpn_path(cfg)
            # 滚动导入窗 与 证书 notAfter 取更早：有 imported_at 时也曾只看导入钟，
            # 导致证书已过期仍「跳过续期」（2026-09-28：notAfter 22:03 已过，脚本仍等到次日 09:34）
            needs_renew = import_needs_renewal(
                state,
                renew_after_hours=cfg["renew_after_hours"],
                ovpn_path=cached,
            )
            if cached.is_file():
                cert_due = cert_needs_renewal(
                    cached, within_minutes=cfg["cert_renew_before_minutes"]
                )
                if cert_due and not needs_renew:
                    log.info("证书到期窗口已到，覆盖「导入未满滚动小时」跳过逻辑")
                needs_renew = needs_renew or cert_due
            if (
                not args.dry_run
                and not args.force
                and not args.force_request
                and cached.is_file()
                and already_imported(cached, state)
                and not needs_renew
            ):
                imported = get_imported_at(state, cached)
                nxt = next_renew_at(
                    state,
                    renew_after_hours=cfg["renew_after_hours"],
                    ovpn_path=cached,
                )
                expiry = parse_ovpn_cert_expiry(cached)
                log.info(
                    "当前配置有效，跳过（上次导入 %s UTC，导入滚动续期 %s UTC，"
                    "证书 notAfter %s UTC；--force-request 强制换新）",
                    imported.strftime("%Y-%m-%d %H:%M:%S") if imported else "?",
                    nxt.strftime("%Y-%m-%d %H:%M:%S") if nxt else "?",
                    expiry.strftime("%Y-%m-%d %H:%M:%S") if expiry else "?",
                )
                return 0

            ovpn, reused = run_async_with_retry(
                lambda: obtain_ovpn(cfg, force_request=args.force_request)
            )
            imported_now = False
            if not args.dry_run:
                if reused and not args.force and already_imported(ovpn, state):
                    log.info("本地配置已导入，跳过重复导入")
                else:
                    import_profile(cli, ovpn, cfg["profile_name"], keep=cfg["keep_profiles"])
                    if relaunch:
                        relaunch_openvpn()
                    imported_now = True
            else:
                log.info("[dry-run] 跳过 OpenVPN 导入")
            save_state(ovpn, dry_run=args.dry_run, mode="sync", record_import=imported_now)

        log.info("✅ VPN 同步完成")
        return 0
    except Exception as exc:
        log.error("❌ VPN 同步失败: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
