"""cursor-agent 调度：默认串行；忙时私聊可并行另开 agent。

定案（2026-08-12）：
- 常态 1 任务 1 agent（exclusive lock）
- 长活占着时新私聊 → run_parallel（不抢 exclusive，不 resume 旧 cursor chat）
- 并行有软顶 AGENT_MAX_PARALLEL，防无脑 fork
"""
from __future__ import annotations

import asyncio
import os
import time
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar

T = TypeVar('T')

_agent_lock = asyncio.Lock()
_active_count = 0
_active_guard = asyncio.Lock()
_parallel_sem: asyncio.Semaphore | None = None

_BUSY_FLAG = Path(
    os.environ.get(
        'AGENT_BUS_STATE_DIR',
        str(Path.home() / 'Library/Application Support/youchu-agent-bus/state'),
    )
) / 'youchu_ai_tg_agent_busy.flag'


def _max_parallel() -> int:
    try:
        n = int(os.getenv('AGENT_MAX_PARALLEL', '3'))
    except ValueError:
        n = 3
    return max(1, min(n, 8))


def _parallel_enabled() -> bool:
    return os.getenv('AGENT_PARALLEL_WHEN_BUSY', 'true').strip().lower() in (
        '1', 'true', 'yes', 'on',
    )


def _get_parallel_sem() -> asyncio.Semaphore:
    global _parallel_sem
    if _parallel_sem is None:
        _parallel_sem = asyncio.Semaphore(_max_parallel())
    return _parallel_sem


def _set_busy_flag() -> None:
    try:
        _BUSY_FLAG.parent.mkdir(parents=True, exist_ok=True)
        _BUSY_FLAG.write_text(
            f'pid={os.getpid()} active={_active_count} ts={int(time.time())}\n',
            encoding='utf-8',
        )
    except OSError:
        pass


def _clear_busy_flag_if_idle() -> None:
    if _active_count > 0:
        _set_busy_flag()
        return
    try:
        _BUSY_FLAG.unlink(missing_ok=True)
    except OSError:
        pass


async def _inc_active() -> None:
    global _active_count
    async with _active_guard:
        _active_count += 1
        _set_busy_flag()


async def _dec_active() -> None:
    global _active_count
    async with _active_guard:
        _active_count = max(0, _active_count - 1)
        _clear_busy_flag_if_idle()


def active_agent_count() -> int:
    return _active_count


def is_agent_busy() -> bool:
    """是否有 cursor-agent 在跑（串行锁或并行槽或忙标记）。"""
    if _agent_lock.locked() or _active_count > 0:
        return True
    if _BUSY_FLAG.is_file():
        try:
            return (time.time() - _BUSY_FLAG.stat().st_mtime) <= 600
        except OSError:
            pass
    return False


def should_spawn_parallel_for_dm() -> bool:
    """私聊叠单：已有 agent 忙 → 另开并行（需开关开启）。"""
    return _parallel_enabled() and is_agent_busy()


async def run_locked(coro_factory: Callable[[], Awaitable[T]]) -> T:
    """独占串行（历史默认）：私聊空闲 / 群聊 / bus 派单 / 学习。"""
    await _inc_active()
    try:
        async with _agent_lock:
            return await coro_factory()
    finally:
        await _dec_active()


async def run_parallel(coro_factory: Callable[[], Awaitable[T]]) -> T:
    """并行槽：不抢 exclusive lock，可与长活并存；受 AGENT_MAX_PARALLEL 限制。"""
    await _inc_active()
    try:
        async with _get_parallel_sem():
            return await coro_factory()
    finally:
        await _dec_active()
