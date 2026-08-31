"""TG 直连指令：不经 AI Agent，秒级执行（如回复工作狂人）。"""
from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass

import context_bridge
import work_memory
from message_style import format_outgoing_block
from agent_bus_client import bus_configured, send_message
from config import AGENT_BUS_AGENT_NAME
from task_provenance import complete_task, register_task

log = logging.getLogger(__name__)

_REPLY_ANT_RE = re.compile(
    r'^(?:回复|告诉|转发给|发给|跟|对)\s*工作狂人\s*[：:]\s*(.+)$',
    re.DOTALL | re.IGNORECASE,
)
_ASK_ANT_DIRECT_RE = re.compile(
    r'^问\s*工作狂人\s*[：:]\s*(.+)$',
    re.DOTALL | re.IGNORECASE,
)
# 自然语言：「把…问一下狂人，…」「帮我问狂人…」
_ASK_KUANGREN_RELAY_RE = re.compile(
    r'问(?:一下|下)?(?:工作)?狂人',
    re.IGNORECASE,
)


def _build_relay_question(text: str) -> str | None:
    """从自然语言抽出要转问狂人的正文。"""
    t = (text or '').strip()
    if not t or not _ASK_KUANGREN_RELAY_RE.search(t):
        return None
    m = re.search(
        r'把(.+?)[，,]\s*问(?:一下|下)?(?:工作)?狂人[，,]\s*(.+)$',
        t,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        return f'{m.group(1).strip()}：{m.group(2).strip()}'
    m = re.search(r'狂人[，,：:\s]+(.+)$', t, re.DOTALL)
    if m and len(m.group(1).strip()) >= 4:
        return m.group(1).strip()
    cleaned = re.sub(
        r'^.*?(?:帮|请|麻烦)?(?:我)?(?:把)?.*?问(?:一下|下)?(?:工作)?狂人[，,：:\s]*',
        '',
        t,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()
    return cleaned or t


@dataclass
class DirectCommand:
    kind: str  # reply_ant | ask_ant
    body: str


def parse(text: str) -> DirectCommand | None:
    t = (text or '').strip()
    if not t:
        return None
    m = _REPLY_ANT_RE.match(t)
    if m:
        body = m.group(1).strip()
        if body:
            return DirectCommand(kind='reply_ant', body=body)
    m = _ASK_ANT_DIRECT_RE.match(t)
    if m:
        body = m.group(1).strip()
        if body:
            return DirectCommand(kind='ask_ant', body=body)
    relay = _build_relay_question(t)
    if relay:
        return DirectCommand(kind='ask_ant', body=f'【又初转问】{relay}')
    return None


async def _reply_worker_ant(
    *,
    body: str,
    source: str,
    uid: int,
    task_label: str,
    task_id: str,
) -> str:
    if not bus_configured():
        raise RuntimeError('agent-bus 未配置（缺 dc-platform.json token）')
    result = await asyncio.to_thread(send_message, body)
    bus_id = result.get('id')
    out_task = register_task(
        source='agent_bus_out',
        text=body,
        uid=uid,
        status='in_progress',
        meta={'bus_id': bus_id, 'to_agent': 'worker_ant', 'reply_to': task_label},
    )
    summary = f"已通过 agent-bus 发给工作狂人（bus id={bus_id}，{out_task['label']}）"
    complete_task(out_task['id'], 'completed', summary)
    complete_task(task_id, 'completed', f'bus出 id={bus_id}')
    work_memory.append_work_record(
        uid=uid,
        question=f"[{task_label}] 回复工作狂人：{body[:200]}",
        result_summary=summary,
        task_id=task_id,
        source=source,
        has_sql=False,
    )
    context_bridge.append_exchange(
        uid=uid,
        question=f"[{task_label}] 回复工作狂人：{body[:400]}",
        answer=summary,
        source=source,
    )
    log.info("[direct] reply_ant %s → bus id=%s text=%s", task_label, bus_id, body[:80])
    return format_outgoing_block(
        '已转发给狂人',
        f'bus id={bus_id}\n\n{body}',
    )


async def _ask_worker_ant_direct(
    *,
    body: str,
    source: str,
    uid: int,
    task_label: str,
    task_id: str,
) -> str:
    from worker_ant_bus import ask_outcome_title, ask_worker_ant_via_bus, bus_ask_ready

    if not bus_ask_ready():
        raise RuntimeError('agent-bus 未配置（需 dc-platform.json 的 base_url + token）')
    reply = await ask_worker_ant_via_bus(body)
    complete_task(task_id, 'completed', reply[:500])
    work_memory.append_work_record(
        uid=uid,
        question=f"[{task_label}] 问工作狂人：{body[:200]}",
        result_summary=reply[:800],
        task_id=task_id,
        source=source,
        has_sql=False,
    )
    context_bridge.append_exchange(
        uid=uid,
        question=f"[{task_label}] 问工作狂人：{body[:400]}",
        answer=reply[:1200],
        source=source,
    )
    return format_outgoing_block(ask_outcome_title(reply), reply)


async def execute(
    cmd: DirectCommand,
    *,
    source: str,
    uid: int,
    task_rec: dict,
) -> str:
    label = task_rec.get('label', '?')
    tid = task_rec['id']
    if cmd.kind == 'reply_ant':
        return await _reply_worker_ant(
            body=cmd.body,
            source=source,
            uid=uid,
            task_label=label,
            task_id=tid,
        )
    if cmd.kind == 'ask_ant':
        return await _ask_worker_ant_direct(
            body=cmd.body,
            source=source,
            uid=uid,
            task_label=label,
            task_id=tid,
        )
    raise RuntimeError(f'未知指令类型: {cmd.kind}')
