#!/usr/bin/env python3
"""OneHR 打卡日历：周日 / 法定节假日 / 主人请假日跳过。

与 omdb/tgbot/cn_punch_calendar.py 同口径，但无 dotenv / tgbot config 依赖，
便于双机 memory 同步后在 ~/.dc-platform/scripts 直接跑。
VPN 续期不要用本模块。
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

BJ = ZoneInfo("Asia/Shanghai")

_LEAVE_CANDIDATES = (
    Path.home() / "Desktop/CHcode/omdb/tgbot/data/personal_leave_dates.json",
    Path("/Users/mac/Desktop/CHcode/omdb/tgbot/data/personal_leave_dates.json"),
)


def _range(year: int, month: int, start: int, end: int) -> list[date]:
    return [date(year, month, d) for d in range(start, end + 1)]


# 国务院放假安排摘录（无 chinese_calendar 时的兜底；仅法定放假日）
_FALLBACK_LEGAL_HOLIDAYS: frozenset[date] = frozenset(
    [
        *_range(2025, 1, 1, 1),
        *_range(2025, 1, 28, 31),
        *_range(2025, 2, 1, 4),
        *_range(2025, 4, 4, 6),
        *_range(2025, 5, 1, 5),
        *_range(2025, 5, 31, 31),
        *_range(2025, 6, 1, 2),
        *_range(2025, 10, 1, 8),
        *_range(2026, 1, 1, 3),
        *_range(2026, 2, 15, 23),
        *_range(2026, 4, 4, 6),
        *_range(2026, 5, 1, 5),
        *_range(2026, 6, 19, 21),
        *_range(2026, 9, 25, 27),
        *_range(2026, 10, 1, 7),  # 国庆
        *_range(2027, 1, 1, 3),
        *_range(2027, 2, 5, 11),
        *_range(2027, 4, 3, 5),
        *_range(2027, 5, 1, 5),
        *_range(2027, 6, 9, 11),
        *_range(2027, 9, 15, 17),
        *_range(2027, 10, 1, 7),
    ]
)


def _today_bj() -> date:
    from datetime import datetime

    return datetime.now(BJ).date()


def _legal_holiday_via_chinese_calendar(day: date) -> tuple[bool, str]:
    try:
        from chinese_calendar import get_holiday_detail
    except ImportError:
        return False, ""
    try:
        on_holiday, name = get_holiday_detail(day)
    except NotImplementedError:
        return False, ""
    if on_holiday and name:
        return True, str(name)
    return False, ""


def _leave_path() -> Path | None:
    for p in _LEAVE_CANDIDATES:
        if p.is_file():
            return p
    return None


def is_personal_leave(day: date | None = None) -> tuple[bool, str]:
    d = day or _today_bj()
    path = _leave_path()
    if not path:
        return False, ""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, ""
    entry = (data.get("dates") or {}).get(d.isoformat()) if isinstance(data, dict) else None
    if not entry:
        return False, ""
    if isinstance(entry, dict):
        note = str(entry.get("reason") or entry.get("note") or "personal leave")
    else:
        note = "personal leave"
    return True, f"leave:{note}"


def should_skip_punch(day: date | None = None) -> tuple[bool, str]:
    """是否跳过 OneHR 签到/签退。返回 (skip, reason)。"""
    d = day or _today_bj()
    leave, leave_reason = is_personal_leave(d)
    if leave:
        return True, leave_reason
    if d.weekday() == 6:
        return True, "sunday"
    ok, name = _legal_holiday_via_chinese_calendar(d)
    if ok:
        return True, f"holiday:{name}"
    if d in _FALLBACK_LEGAL_HOLIDAYS:
        return True, "holiday:fallback"
    return False, ""
