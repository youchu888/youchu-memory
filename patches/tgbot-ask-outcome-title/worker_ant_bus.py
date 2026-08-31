"""经 agent-bus 与工作狂人互通（发消息 / 问完等回复）。

等待规则：超过 AGENT_BUS_NUDGE_AFTER_SEC（默认 5 分钟）仍无实质回复 → 催促 1 次，不硬等沉默。
"""
from __future__ import annotations

import asyncio
import logging
import time

from agent_bus_client import bus_configured, fetch_inbox, load_offset, send_message
from config import (
    AGENT_BUS_ASK_POLL_INTERVAL,
    AGENT_BUS_ASK_TIMEOUT,
    AGENT_BUS_NUDGE_AFTER_SEC,
)

log = logging.getLogger(__name__)

WORKER_ANT_AGENT = 'worker_ant'


def bus_ask_ready() -> bool:
    return bus_configured()


def _is_substantive_reply(text: str, *, outbound_bus_id: int) -> bool:
    """过滤纯 ACK / 探活，不算「审完/答完」。"""
    t = (text or '').strip()
    if not t:
        return False
    low = t.lower()
    # 仅 ACK、无结论
    if low.startswith('[ack') and ('开审' in t or '收到' in t) and '结论' not in t and 'PASS' not in t and 'GO' not in t and '退回' not in t:
        if len(t) < 220:
            return False
    if t in ('收到', '在', 'OK', 'ok', '嗯'):
        return False
    return True


async def send_to_worker_ant(text: str) -> dict:
    """单向发送，返回 {id, ...}。"""
    if not bus_configured():
        raise RuntimeError('agent-bus 未配置（需 .claude/database/dc-platform.json）')
    return await asyncio.to_thread(send_message, text, to_agent=WORKER_ANT_AGENT)


async def ask_worker_ant_via_bus(
    question: str,
    *,
    timeout: int | None = None,
    wait_reply: bool = True,
    nudge_after_sec: int | None = None,
) -> str:
    """经 agent-bus 提问；可选轮询 inbox 等工作狂人回复。

    超过 nudge_after_sec（默认 5 分钟）仍无实质回复 → 催促 1 次，继续等到 timeout。
    """
    if not bus_configured():
        raise RuntimeError('agent-bus 未配置（需 .claude/database/dc-platform.json）')

    q = (question or '').strip()
    if not q:
        raise ValueError('问题不能为空')

    after_before = load_offset()
    result = await send_to_worker_ant(q)
    bus_id = int(result.get('id') or 0)

    if not wait_reply:
        return f'已通过 agent-bus 发给工作狂人（bus id={bus_id}），回复会私聊通知你。'

    deadline = time.time() + (timeout or AGENT_BUS_ASK_TIMEOUT)
    nudge_sec = AGENT_BUS_NUDGE_AFTER_SEC if nudge_after_sec is None else nudge_after_sec
    nudged = False
    started = time.time()

    while time.time() < deadline:
        data = await asyncio.to_thread(fetch_inbox, after_before)
        for msg in data.get('messages') or []:
            mid = int(msg.get('id') or 0)
            if bus_id and mid <= bus_id:
                continue
            if (msg.get('from_agent') or '').strip() != WORKER_ANT_AGENT:
                continue
            reply = (msg.get('text') or '').strip()
            if reply and _is_substantive_reply(reply, outbound_bus_id=bus_id):
                log.info('[agent-bus] ask got reply bus_id=%s reply_id=%s', bus_id, mid)
                return reply
        # 超 5 分钟无实质回复 → 催促一次
        if (
            not nudged
            and nudge_sec > 0
            and (time.time() - started) >= nudge_sec
        ):
            nudged = True
            nudge_text = (
                f'[催促] bus#{bus_id} 发出已超 {nudge_sec // 60} 分钟未见实质回复。'
                f'请尽快回结论（PASS/退回/GO/HOLD 均可）；我这边不硬等。'
            )
            try:
                nudge_res = await send_to_worker_ant(nudge_text)
                log.info(
                    '[agent-bus] nudged worker_ant for bus#%s → outbound=%s',
                    bus_id,
                    nudge_res.get('id'),
                )
            except Exception as exc:
                log.warning('[agent-bus] nudge failed bus#%s: %s', bus_id, exc)
        await asyncio.sleep(AGENT_BUS_ASK_POLL_INTERVAL)

    waited = timeout or AGENT_BUS_ASK_TIMEOUT
    extra = '（已催促 1 次）' if nudged else ''
    return (
        f'已通过 agent-bus 发给工作狂人（bus id={bus_id}）。'
        f'等待 {waited}s 内未收到实质回复{extra}，狂人回话后会私聊通知你。'
    )


def ask_outcome_title(reply: str) -> str:
    """TG 出站标题：超时/仅发送时勿标「狂人回复」。"""
    if (reply or '').strip().startswith('已通过 agent-bus 发给工作狂人'):
        return '已转问狂人'
    return '狂人回复'
