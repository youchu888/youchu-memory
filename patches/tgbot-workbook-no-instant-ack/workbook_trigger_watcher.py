"""工作簿触发：只扫 bus 入站，实查后 reply。不回群。"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import (
    AGENT_BUS_AGENT_NAME,
    AGENT_BUS_STATE_DIR,
    GROUP_WORKBOOK_PROGRESS_ENABLED,
)
import group_workbook_progress_handler as wb

log = logging.getLogger(__name__)
_BJ = ZoneInfo('Asia/Shanghai')
_POLL_SEC = 20


def _status_path() -> Path:
    return Path(AGENT_BUS_STATE_DIR) / f'{AGENT_BUS_AGENT_NAME}_tg_status.jsonl'


def _inbox_path() -> Path:
    return Path(AGENT_BUS_STATE_DIR) / f'{AGENT_BUS_AGENT_NAME}_inbox.jsonl'


def _offset_path() -> Path:
    return Path(AGENT_BUS_STATE_DIR) / f'{AGENT_BUS_AGENT_NAME}_workbook_watcher.offset'


def _bus_offset_path() -> Path:
    return Path(AGENT_BUS_STATE_DIR) / f'{AGENT_BUS_AGENT_NAME}_workbook_bus.offset'


def _load_offset(path: Path, source: Path) -> int:
    if not path.is_file():
        if source.is_file():
            try:
                with source.open(encoding='utf-8') as f:
                    end = sum(1 for _ in f)
                _save_offset(path, end)
                return end
            except OSError:
                pass
        return 0
    try:
        return int(path.read_text(encoding='utf-8').strip() or '0')
    except ValueError:
        return 0


def _save_offset(path: Path, n: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(n), encoding='utf-8')


def _scan_status_incoming() -> list[dict]:
    path = _status_path()
    if not path.is_file():
        return []
    offset = _load_offset(_offset_path(), path)
    jobs: list[dict] = []
    line_no = 0
    with path.open(encoding='utf-8') as f:
        for raw in f:
            line_no += 1
            if line_no <= offset:
                continue
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if ev.get('type') != 'incoming':
                continue
            body = ev.get('text') or ''
            if not wb.is_workbook_roll_call(body) or wb.looks_like_canned_fallback(body):
                continue
            ts = (ev.get('ts') or ev.get('created_at') or '')[:10]
            today = datetime.now(_BJ).strftime('%Y-%m-%d')
            if ts and ts != today:
                continue
            jobs.append({
                'text': body,
                'msg_id': int(ev.get('msg_id') or 0),
                'source': f"tg_status:{ev.get('channel')}",
            })
    _save_offset(_offset_path(), line_no)
    return jobs


def _scan_bus_inbox() -> list[dict]:
    path = _inbox_path()
    if not path.is_file():
        return []
    offset = _load_offset(_bus_offset_path(), path)
    jobs: list[dict] = []
    line_no = 0
    today = datetime.now(_BJ).strftime('%Y-%m-%d')
    with path.open(encoding='utf-8') as f:
        for raw in f:
            line_no += 1
            if line_no <= offset:
                continue
            raw = raw.strip()
            if not raw:
                continue
            try:
                ev = json.loads(raw)
            except json.JSONDecodeError:
                continue
            from_agent = (ev.get('from_agent') or '').strip()
            if from_agent not in {'worker_ant', 'worker_ant_bot'}:
                continue
            body = ev.get('text') or ''
            if not wb.is_workbook_roll_call(body) or wb.looks_like_canned_fallback(body):
                continue
            created = str(ev.get('created_at') or ev.get('ts') or '')
            if created[:10] and created[:10] != today:
                continue
            bus_id = int(ev.get('id') or ev.get('bus_id') or 0)
            if not bus_id:
                continue
            jobs.append({'text': body, 'bus_id': bus_id})
    _save_offset(_bus_offset_path(), line_no)
    return jobs


async def _watcher_loop(application) -> None:
    wb.set_application(application)
    log.info('[workbook-watcher] started poll=%ss (bus-only; no group reply)', _POLL_SEC)
    while True:
        try:
            bus_jobs = await asyncio.to_thread(_scan_bus_inbox)
            for job in bus_jobs:
                asyncio.create_task(
                    wb.reply_workbook_via_bus(job['text'], bus_id=job['bus_id']),
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.exception('[workbook-watcher] loop error: %s', exc)
        await asyncio.sleep(_POLL_SEC)


async def start_workbook_watcher(application) -> None:
    if not GROUP_WORKBOOK_PROGRESS_ENABLED:
        log.info('[workbook-watcher] disabled')
        return
    wb.set_application(application)
    asyncio.create_task(_watcher_loop(application))
