#!/usr/bin/env python3
"""OneHR 打卡调度：对齐极客打卡规则（窗口内随机时刻，每天各打一次）。

与 omdb/tgbot/jike_checkin_watcher.py 同思路：
  - 上班 Mon-Sat 在 ONEHR_CHECKIN_WINDOW 内随机
  - 下班 Mon-Fri ONEHR_CHECKOUT_WINDOW；周六 ONEHR_CHECKOUT_SAT_WINDOW
  - 周日不调度
  - 到计划时刻后调用 onehr_checkin_auto.py 实际上传（仍以 API status=due 为准）
"""

from __future__ import annotations

import argparse
import secrets
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")
DEFAULT_ENV = Path.home() / ".dc-platform/config/onehr.env"
AUTO_PY = Path.home() / ".dc-platform/scripts/onehr_checkin_auto.py"
STATE_FILE = Path.home() / ".dc-platform/onehr/schedule_state.json"
LOG_DIR = Path.home() / ".dc-platform/onehr/logs"
_PLAN_PREFIX = "_plan_"
_KEEP_PLAN_DAYS = 3


def load_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def log(msg: str) -> None:
    ts = datetime.now(BJ).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [onehr-schedule] {msg}"
    print(line, flush=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (LOG_DIR / "scheduler.log").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _parse_hhmm(s: str) -> Optional[Tuple[int, int]]:
    parts = (s or "").strip().split(":")
    if len(parts) != 2:
        return None
    try:
        h, m = int(parts[0]), int(parts[1])
        if h == 24 and m == 0:
            return 24, 0
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
    except ValueError:
        pass
    return None


def window_bounds(start_hhmm: str, end_hhmm: str, day: date) -> Optional[Tuple[datetime, datetime]]:
    sp, ep = _parse_hhmm(start_hhmm), _parse_hhmm(end_hhmm)
    if not sp or not ep:
        return None
    sh, sm = sp
    eh, em = ep
    start = datetime(day.year, day.month, day.day, sh, sm, tzinfo=BJ)
    if eh == 24 and em == 0:
        end = datetime(day.year, day.month, day.day, tzinfo=BJ) + timedelta(days=1)
    elif eh < sh or (eh == sh and em <= sm):
        # 跨日：如 22:00-03:00
        end = datetime(day.year, day.month, day.day, eh, em, tzinfo=BJ) + timedelta(days=1)
    else:
        end = datetime(day.year, day.month, day.day, eh, em, tzinfo=BJ)
    if end <= start:
        return None
    return start, end


def random_in_window(start: datetime, end: datetime) -> datetime:
    span = int((end - start).total_seconds())
    if span <= 0:
        return start
    return start + timedelta(seconds=secrets.randbelow(span + 1))


def load_state() -> dict:
    if STATE_FILE.is_file():
        try:
            import json

            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    import json

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def plan_key(kind: str, day: date) -> str:
    return f"{kind}{_PLAN_PREFIX}{day.isoformat()}"


def purge_stale_plans(state: dict, today: date) -> bool:
    changed = False
    cutoff = today - timedelta(days=_KEEP_PLAN_DAYS)
    for key in list(state.keys()):
        if _PLAN_PREFIX not in key:
            continue
        day_str = key.rsplit(_PLAN_PREFIX, 1)[-1]
        try:
            if date.fromisoformat(day_str) < cutoff:
                del state[key]
                changed = True
        except ValueError:
            continue
    return changed


def already_punched(kind: str, day: date) -> bool:
    return load_state().get(kind) == day.isoformat()


def mark_punched(kind: str, day: date) -> None:
    state = load_state()
    state[kind] = day.isoformat()
    save_state(state)


def checkout_window(cfg: dict, day: date) -> Optional[Tuple[str, str]]:
    wd = day.weekday()  # Mon=0 … Sun=6
    if wd == 6:
        return None
    if wd == 5:
        return (
            cfg.get("ONEHR_CHECKOUT_SAT_WINDOW_START", "19:00"),
            cfg.get("ONEHR_CHECKOUT_SAT_WINDOW_END", "19:30"),
        )
    return (
        cfg.get("ONEHR_CHECKOUT_WINDOW_START", "22:00"),
        cfg.get("ONEHR_CHECKOUT_WINDOW_END", "22:30"),
    )


def checkin_window(cfg: dict, day: date) -> Optional[Tuple[str, str]]:
    if day.weekday() == 6:
        return None
    return (
        cfg.get("ONEHR_CHECKIN_WINDOW_START", "09:30"),
        cfg.get("ONEHR_CHECKIN_WINDOW_END", "10:00"),
    )


def ensure_daily_plans(cfg: dict, day: date, *, force_new: bool = False) -> Dict[str, datetime]:
    state = load_state()
    changed = purge_stale_plans(state, day)
    planned: Dict[str, datetime] = {}

    specs = []
    cw = checkin_window(cfg, day)
    if cw:
        specs.append(("checkin", cw[0], cw[1]))
    cow = checkout_window(cfg, day)
    if cow:
        specs.append(("checkout", cow[0], cow[1]))

    for kind, ws, we in specs:
        key = plan_key(kind, day)
        bounds = window_bounds(ws, we, day)
        if not bounds:
            continue
        start, end = bounds

        if not force_new and key in state:
            try:
                saved = datetime.fromisoformat(state[key])
                if saved.tzinfo is None:
                    saved = saved.replace(tzinfo=BJ)
                if start <= saved < end:
                    planned[kind] = saved
                    continue
            except ValueError:
                pass

        when = random_in_window(start, end)
        state[key] = when.isoformat()
        planned[kind] = when
        changed = True

    if changed:
        save_state(state)
    return planned


def next_planned_run(cfg: dict, kind: str, now: datetime) -> Optional[datetime]:
    today = now.date()
    if already_punched(kind, today):
        return None

    if kind == "checkin":
        win = checkin_window(cfg, today)
    else:
        win = checkout_window(cfg, today)
    if not win:
        return None

    ws, we = win
    bounds = window_bounds(ws, we, today)
    if not bounds:
        return None
    start, end = bounds

    target_day = today
    if now >= end:
        return None
    if now < start:
        target_day = today
    else:
        target_day = today

    plans = ensure_daily_plans(cfg, target_day)
    planned = plans.get(kind)
    if not planned:
        return None

    if planned < now:
        effective_start = max(now, start)
        if effective_start >= end:
            return None
        planned = random_in_window(effective_start, end)
        state = load_state()
        state[plan_key(kind, target_day)] = planned.isoformat()
        save_state(state)
    return planned


def notify_mac(title: str, message: str) -> None:
    safe_title = title.replace('"', '\\"')
    safe_msg = message.replace('"', '\\"')
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe_msg}" with title "{safe_title}"'],
        check=False,
        capture_output=True,
    )


def in_window_now(cfg: dict, kind: str, now: datetime) -> bool:
    day = now.date()
    win = checkin_window(cfg, day) if kind == "checkin" else checkout_window(cfg, day)
    if not win:
        return False
    bounds = window_bounds(win[0], win[1], day)
    if not bounds:
        return False
    start, end = bounds
    return start <= now < end


def invalidate_plan(kind: str, day: date) -> None:
    state = load_state()
    key = plan_key(kind, day)
    if key in state:
        del state[key]
        save_state(state)


def sync_from_server(env_path: Path) -> None:
    subprocess.run(
        [sys.executable, "-u", str(AUTO_PY), "--env", str(env_path), "--sync-schedule"],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )


def check_missed_windows(cfg: dict, now: datetime, env_path: Path) -> None:
    """窗口已结束但未标记打卡 → 通知一次（先同步服务端状态）。"""
    sync_from_server(env_path)
    today = now.date()
    state = load_state()
    for kind in ("checkin", "checkout"):
        if already_punched(kind, today):
            continue
        win = checkin_window(cfg, today) if kind == "checkin" else checkout_window(cfg, today)
        if not win:
            continue
        bounds = window_bounds(win[0], win[1], today)
        if not bounds:
            continue
        _, end = bounds
        if now < end:
            continue
        flag = f"_missed_{kind}_{today.isoformat()}"
        if state.get(flag):
            continue
        state[flag] = True
        save_state(state)
        label = "上班" if kind == "checkin" else "下班"
        log(f"WARN {label}窗口已结束但未打卡")
        notify_mac("OneHR 打卡遗漏", f"{label}窗 {win[0]}-{win[1]} 已过，请手动补卡")


def run_punch(env_path: Path, kind: str, cfg: dict) -> bool:
    extra = secrets.randbelow(115) + 5
    log(f"{kind} 计划触发，额外随机延迟 {extra}s")
    time.sleep(extra)

    proc = subprocess.run(
        [sys.executable, "-u", str(AUTO_PY), "--env", str(env_path), "--kind", kind],
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    for line in out.splitlines():
        if line.strip():
            log(line.strip())
    now = datetime.now(BJ)
    if proc.returncode == 0:
        mark_punched(kind, now.date())
        return True
    if proc.returncode == 2:
        log(f"{kind} 窗口未到或暂不可打")
    else:
        log(f"{kind} 失败 exit={proc.returncode}，窗口内将重试")
        notify_mac("OneHR 打卡失败", f"{kind} 自动打卡失败，窗口内会重试")
    if in_window_now(cfg, kind, now):
        invalidate_plan(kind, now.date())
    return False


def scheduler_loop(env_path: Path, cfg: dict) -> None:
    log(
        "started "
        f"checkin={cfg.get('ONEHR_CHECKIN_WINDOW_START', '09:30')}"
        f"~{cfg.get('ONEHR_CHECKIN_WINDOW_END', '10:00')} "
        f"checkout={cfg.get('ONEHR_CHECKOUT_WINDOW_START', '22:00')}"
        f"~{cfg.get('ONEHR_CHECKOUT_WINDOW_END', '22:30')} "
        f"sat_checkout={cfg.get('ONEHR_CHECKOUT_SAT_WINDOW_START', '19:00')}"
        f"~{cfg.get('ONEHR_CHECKOUT_SAT_WINDOW_END', '19:30')} "
        "(daily random, 同极客规则)"
    )
    last_plan_day: Optional[date] = None

    while True:
        try:
            now = datetime.now(BJ)
            today = now.date()

            if last_plan_day != today:
                plans = ensure_daily_plans(cfg, today)
                if plans:
                    parts = [f"{k}={v.strftime('%H:%M:%S')}" for k, v in sorted(plans.items())]
                    log(f"today plan {', '.join(parts)}")
                tomorrow = today + timedelta(days=1)
                if tomorrow.weekday() != 6:
                    ensure_daily_plans(cfg, tomorrow)
                last_plan_day = today

            check_missed_windows(cfg, now, env_path)

            targets = []
            for kind in ("checkin", "checkout"):
                nxt = next_planned_run(cfg, kind, now)
                if nxt:
                    targets.append((nxt, kind))

            if not targets:
                time.sleep(300)
                continue

            targets.sort(key=lambda x: x[0])
            wait_sec = max(1.0, (targets[0][0] - now).total_seconds())
            log(f"next {targets[0][1]} in {wait_sec:.0f}s")
            time.sleep(wait_sec)
            run_punch(env_path, targets[0][1], cfg)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            log(f"loop error: {exc}")
            time.sleep(60)


def main() -> int:
    parser = argparse.ArgumentParser(description="OneHR 打卡调度（极客同款随机窗）")
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--show-plan", action="store_true", help="打印今日/明日计划后退出")
    args = parser.parse_args()

    if not args.env.is_file():
        raise SystemExit(f"缺少 {args.env}")

    cfg = load_env(args.env)

    if args.show_plan:
        today = datetime.now(BJ).date()
        for d in (today, today + timedelta(days=1)):
            plans = ensure_daily_plans(cfg, d)
            wd_names = "一二三四五六日"
            label = wd_names[d.weekday()]
            if d.weekday() == 6:
                print(f"{d} 周日：无计划")
                continue
            parts = [f"{k}={v.strftime('%H:%M:%S')}" for k, v in sorted(plans.items())]
            print(f"{d} 周{label}: {', '.join(parts) if parts else '无'}")
        return 0

    scheduler_loop(args.env, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
