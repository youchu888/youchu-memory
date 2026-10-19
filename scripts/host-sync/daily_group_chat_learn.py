#!/usr/bin/env python3
"""每日群聊和私聊分类、梳理、沉淀。

定时：每天上海 02:00 读上一自然日。
先让已连接的真人号把当前所在的每一个群、每一条私聊、这一天的全部文字拉下来，
再读 data/group_raw/YYYY-MM-DD.jsonl，并补上当日 worker_ant 群入站。
不另开 Telegram session。

沉淀：带明确规矩的句子当天入库；同一句话隔日再出现则升级已有 lesson。
没做完的需求写入未做清单；已经统一的指标写入记忆。
私聊里非闲聊，以及群里的需求、口径和讨论，各写一行到聊天参考，做事时按关键词查。
学完把短汇总推到私聊。不写 work-log、不进日报、不进工作簿进展。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TGBOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TGBOT_DIR)

import db  # noqa: E402
from config import (  # noqa: E402
    ALLOWED_USERS,
    TG_BOT_TOKEN,
    TGBOT_DIR as _TGBOT,
    WORKER_ANT_INBOX_PATH,
)
from group_message_capture import DONE_PATH, RAW_DIR, REQUEST_PATH, SHANGHAI  # noqa: E402

LEARN_ROOT = os.path.expanduser('~/.dc-platform/memory/group_chat/learn')
OPEN_REQ_PATH = os.path.expanduser('~/.dc-platform/memory/group_chat/open_requirements.md')
SETTLED_PATH = os.path.expanduser('~/.dc-platform/memory/group_chat/metrics_settled.md')
REF_PATH = os.path.expanduser('~/.dc-platform/memory/group_chat/reference.md')
STATE_PATH = os.path.join(_TGBOT, 'data', 'group_learn_state.json')
MAX_NEW = 12
MAX_UPGRADE = 8

_NOISE = re.compile(
    r'^(收到|好的|好|嗯+|ok|OK|1|在|在的|谢谢|辛苦了?|哈哈+|\[OK\])[！!。.\s]*$',
    re.IGNORECASE,
)
_SKIP_SENDER = re.compile(r'youchu_ai_bot|youchu8888', re.IGNORECASE)
_RULE = re.compile(r'(禁止|不得|必须|须|不要|只算|只计|口径|拍板|定案|不能|勿|已核|审核通过|修改后通过|已统一|统一为|统一成)')
_OPEN_REQ = re.compile(r'(需要返回|能加上|一起返回|还没做|还没加|待补|下周再说|下周就|要返回|要加|能不能|是否可以)')
_DISCUSS = re.compile(r'[？?]|怎么|为什么|要不要|能不能|是不是|对不上|看一下|讨论|建议')
_DONE_REQ = re.compile(r'(已经加上|已返回|已完成|做完了)')
_SETTLED = re.compile(r'(口径统一|已统一|统一为|统一成|就按这个口径|定案)')
_CATEGORIES: list[tuple[str, re.Pattern[str]]] = [
    ('审核', re.compile(r'审核|审完|修改后通过|审核通过|打回|HOLD|bus#\d+')),
    ('口径', re.compile(r'口径|定义为|算作|只算|只计|禁止|不得|必须')),
    ('事故', re.compile(r'失败|FAILURE|断流|告警|挂了|OOM|事故')),
    ('发布', re.compile(r'发产|上线|补数|海豚|挂编排|首跑|建表')),
    ('分工', re.compile(r'负责|主责|归.+|工作簿|勿抢|分工|待办')),
    ('需求', re.compile(r'需要返回|能加上|一起返回|还没做|还没加|待补')),
]
_TABLE = re.compile(r'\b((?:dw|dwd|dwm|dws|ads|dim)\.[a-z][a-z0-9_]*|[a-z][a-z0-9]*_[a-z0-9_]+)\b')


def _today() -> str:
    return datetime.now(SHANGHAI).strftime('%Y-%m-%d')


def _read_jsonl(path: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    rows: list[dict] = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _shanghai_day(ts: str) -> str:
    ts = (ts or '').strip()
    if not ts:
        return ''
    if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', ts):
        return ts[:10]
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except ValueError:
        return ts[:10]
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    return dt.astimezone(SHANGHAI).strftime('%Y-%m-%d')


def _request_history(day: str, timeout_sec: float = 1200) -> dict:
    """请正在跑的真人号把这一天每个群和每条私聊的文字拉全。超时就带着已有落盘继续，并在汇总里写明。"""
    nonce = uuid.uuid4().hex
    req = {
        'day': day,
        'nonce': nonce,
        'requested_at': datetime.now(SHANGHAI).isoformat(timespec='seconds'),
    }
    os.makedirs(os.path.dirname(REQUEST_PATH), exist_ok=True)
    tmp = REQUEST_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(req, f, ensure_ascii=False)
    os.replace(tmp, REQUEST_PATH)
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if os.path.isfile(DONE_PATH):
            try:
                with open(DONE_PATH, encoding='utf-8') as f:
                    done = json.load(f)
            except (OSError, json.JSONDecodeError):
                done = {}
            if done.get('nonce') == nonce:
                return done
        time.sleep(2)
    return {'ok': False, 'error': 'timeout', 'day': day, 'nonce': nonce}


def _chat_counts(messages: list[dict]) -> list[tuple[str, int]]:
    counts: dict[str, int] = defaultdict(int)
    for rec in messages:
        title = (rec.get('chat_title') or '').strip() or str(rec.get('chat_id') or '未知群')
        counts[title] += 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _load_messages(day: str) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []

    def push(rec: dict, source: str) -> None:
        text = (rec.get('text') or '').strip()
        if not text:
            return
        key = f"{rec.get('chat_id')}:{rec.get('message_id')}"
        if not rec.get('message_id'):
            key = hashlib.sha1(text.encode()).hexdigest()[:16]
        if key in seen:
            return
        seen.add(key)
        out.append({
            'ts': rec.get('ts') or rec.get('ts_utc') or '',
            'chat_id': rec.get('chat_id'),
            'chat_kind': rec.get('chat_kind') or 'group',
            'chat_title': rec.get('chat_title') or '',
            'message_id': rec.get('message_id'),
            'sender_username': rec.get('sender_username') or '',
            'sender_name': rec.get('sender_name') or '',
            'text': text,
            'source': source,
        })

    for rec in _read_jsonl(os.path.join(RAW_DIR, f'{day}.jsonl')):
        push(rec, 'group_raw')
    for rec in _read_jsonl(WORKER_ANT_INBOX_PATH):
        if _shanghai_day(rec.get('ts') or '') != day:
            continue
        push(rec, 'worker_ant_inbox')
    out.sort(key=lambda r: r.get('ts') or '')
    return out


def classify(text: str) -> str:
    for name, pat in _CATEGORIES:
        if pat.search(text):
            return name
    return '其他'


def _scope(text: str, category: str) -> str:
    m = _TABLE.search(text)
    if m:
        return m.group(1)[:80]
    return f'群聊{category}'


def _rule_line(text: str) -> str:
    parts = re.split(r'[。\n]', text)
    picked = [p.strip() for p in parts if p.strip() and _RULE.search(p)]
    if not picked:
        return ''
    line = '；'.join(picked[:2])
    line = re.sub(r'\s+', ' ', line).strip()
    return line[:240]


def _norm(s: str) -> str:
    return re.sub(r'\s+', '', s or '')


def _fp(text: str) -> str:
    return hashlib.sha1(_norm(text).encode()).hexdigest()[:20]


def _load_state() -> dict:
    if not os.path.isfile(STATE_PATH):
        return {'seen': {}, 'promoted': {}}
    try:
        with open(STATE_PATH, encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {'seen': {}, 'promoted': {}}
        data.setdefault('seen', {})
        data.setdefault('promoted', {})
        return data
    except (OSError, json.JSONDecodeError):
        return {'seen': {}, 'promoted': {}}


def _save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)


def _is_noise(rec: dict) -> bool:
    text = rec.get('text') or ''
    if _NOISE.match(text.strip()):
        return True
    if len(text.strip()) < 12:
        return True
    who = f"{rec.get('sender_username') or ''} {rec.get('sender_name') or ''}"
    if _SKIP_SENDER.search(who):
        return True
    return False


def _one_line(text: str) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()[:180]


def _reference_rows(day: str, messages: list[dict]) -> list[str]:
    """私聊非闲聊都留一行。群里只留需求、口径和实质讨论。"""
    rows: list[str] = []
    for rec in messages:
        if _is_noise(rec):
            continue
        text = rec.get('text') or ''
        title = (rec.get('chat_title') or '').strip()
        private = rec.get('chat_kind') == 'private' or title.startswith('私聊')
        if _OPEN_REQ.search(text) and not _DONE_REQ.search(text):
            kind = '需求'
        elif _SETTLED.search(text):
            kind = '口径'
        elif private or _DISCUSS.search(text) or (_TABLE.search(text) and classify(text) != '其他'):
            kind = '讨论' if classify(text) == '其他' else classify(text)
        else:
            continue
        where = '私聊' if private else '群'
        who = title or (rec.get('sender_name') or '')
        rows.append(f'- {day} | {where} | {kind} | {who} | {_one_line(text)}')
    return rows


def _memory_rows(day: str, messages: list[dict]) -> tuple[list[str], list[str]]:
    opens: list[str] = []
    settled: list[str] = []
    for rec in messages:
        if _is_noise(rec):
            continue
        text = rec.get('text') or ''
        title = rec.get('chat_title') or ''
        kind = '私聊' if rec.get('chat_kind') == 'private' or title.startswith('私聊') else '群'
        line = f'- {day} {kind} {title}：{_one_line(text)}'
        if _OPEN_REQ.search(text) and not _DONE_REQ.search(text):
            opens.append(line)
        if _SETTLED.search(text):
            settled.append(line)
    return opens, settled


def _append_memory(path: str, header: str, bullets: list[str]) -> list[str]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = header if not os.path.isfile(path) else open(path, encoding='utf-8').read()
    added: list[str] = []
    for bullet in bullets:
        if bullet in existing:
            continue
        added.append(bullet)
        if not existing.endswith('\n'):
            existing += '\n'
        existing += bullet + '\n'
    if added or not os.path.isfile(path):
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(existing if existing.endswith('\n') else existing + '\n')
        os.replace(tmp, path)
    return added


def _render(
    day: str,
    buckets: dict[str, list[dict]],
    actions: list[str],
    messages: list[dict],
    history: dict,
    opens: list[str],
    settled: list[str],
) -> str:
    chats = _chat_counts(messages)
    lines = [
        f'# 群聊日学习 · {day}',
        '',
        f'> 生成时间 {datetime.now(SHANGHAI).strftime("%Y-%m-%d %H:%M")}（Asia/Shanghai）',
        '> 来源：这个号当前所在的每一个群和每一条私聊，上一自然日全部文字。闲聊不入库。',
        '',
    ]
    if history.get('ok'):
        lines.append(
            f"> 回拉 {history.get('groups', 0)} 个群、{history.get('privates', 0)} 条私聊，"
            f"扫到 {history.get('scanned', 0)} 条，新落盘 {history.get('written', 0)} 条。"
        )
    else:
        lines.append(f"> 回拉没完成：{history.get('error') or '未知'}。下面只是已经落盘的部分。")
    lines.extend(['', '## 各群条数', ''])
    if chats:
        lines.extend(f'- {title}：{n}' for title, n in chats)
    else:
        lines.append('- 没有读到群消息。')
    lines.extend(['', '## 未做需求', ''])
    if opens:
        lines.extend(opens)
    else:
        lines.append('- 没有新的未做需求。')
    lines.extend(['', '## 已统一指标', ''])
    if settled:
        lines.extend(settled)
    else:
        lines.append('- 没有新的已统一指标。')
    lines.extend(['', '## 沉淀动作', ''])
    if actions:
        lines.extend(f'- {a}' for a in actions)
    else:
        lines.append('- 今日没有新规矩需要入库或升级。')
    order = ['审核', '口径', '事故', '发布', '分工', '需求', '其他']
    for name in order:
        rows = buckets.get(name) or []
        if not rows:
            continue
        lines.extend(['', f'## {name}（{len(rows)}）', ''])
        for rec in rows[:40]:
            who = rec.get('sender_username') or rec.get('sender_name') or '未知'
            title = rec.get('chat_title') or str(rec.get('chat_id') or '')
            body = re.sub(r'\s+', ' ', rec.get('text') or '')[:180]
            lines.append(f'- `{rec.get("ts", "")[:16]}` @{who} {title}：{body}')
        if len(rows) > 40:
            lines.append(f'- …其余 {len(rows) - 40} 条只计数量')
    lines.append('')
    return '\n'.join(lines)


def learn_day(day: str, *, dry_run: bool = False) -> dict:
    history = {'ok': True, 'skipped': True} if dry_run else _request_history(day)
    messages = _load_messages(day)
    buckets: dict[str, list[dict]] = defaultdict(list)
    noise = 0
    for rec in messages:
        if _is_noise(rec):
            noise += 1
            buckets['闲聊'].append(rec)
            continue
        buckets[classify(rec['text'])].append(rec)

    state = _load_state()
    lessons = db.get_public_lessons()
    actions: list[str] = []
    new_n = 0
    up_n = 0

    for rec in messages:
        if _is_noise(rec):
            continue
        category = classify(rec['text'])
        if category == '其他':
            continue
        rule = _rule_line(rec['text'])
        if not rule:
            continue
        scope = _scope(rec['text'], category)
        digest = _fp(rule)
        seen_days = state['seen'].setdefault(digest, [])
        if day not in seen_days:
            seen_days.append(day)
        repeated = len(seen_days) >= 2
        hard = bool(_RULE.search(rule))
        if not hard and not repeated:
            continue
        if digest in state['promoted']:
            continue

        covered_id = None
        upgrade_id = None
        nrule = _norm(rule)
        for row in lessons:
            old = row.get('lesson') or ''
            nold = _norm(old)
            if not nold:
                continue
            if nrule == nold or (len(nrule) >= 24 and nrule in nold):
                covered_id = row['id']
                break
            same_scope = (row.get('scope') or '') == scope
            if same_scope and nold in nrule and len(rule) >= len(old) + 24:
                upgrade_id = row['id']
                break
        if covered_id:
            state['promoted'][digest] = {'lesson_id': covered_id, 'day': day, 'via': 'covered'}
            continue
        if dry_run:
            actions.append(f'[dry-run] {scope}｜{rule[:80]}')
            continue
        if upgrade_id and up_n < MAX_UPGRADE:
            db.upgrade_lesson(upgrade_id, rule)
            up_n += 1
            state['promoted'][digest] = {'lesson_id': upgrade_id, 'day': day, 'via': 'upgrade'}
            actions.append(f'升级 #{upgrade_id} {scope}｜{rule[:80]}')
            for row in lessons:
                if row['id'] == upgrade_id:
                    row['lesson'] = rule
            continue
        if new_n >= MAX_NEW:
            continue
        if db.lesson_exists(scope, rule):
            state['promoted'][digest] = {'day': day, 'via': 'exists'}
            continue
        lid = db.add_lesson(
            owner_user_id=None,
            source='group_daily',
            scope=scope,
            lesson=rule,
            related_question=(rec.get('text') or '')[:400],
        )
        new_n += 1
        lessons.append({'id': lid, 'scope': scope, 'lesson': rule})
        state['promoted'][digest] = {'lesson_id': lid, 'day': day, 'via': 'new'}
        actions.append(f'新入库 #{lid} {scope}｜{rule[:80]}')

    opens, settled = _memory_rows(day, messages)
    references = _reference_rows(day, messages)
    if not dry_run:
        _append_memory(
            OPEN_REQ_PATH,
            '# 未做需求\n\n从群聊和私聊扫到、当时没有做完的要求。做完后把该行状态改成已完成，不要删行。\n',
            opens,
        )
        _append_memory(
            SETTLED_PATH,
            '# 已统一指标\n\n群聊和私聊里已经说定的口径。同一句不重复写。\n',
            settled,
        )
        _append_memory(
            REF_PATH,
            '# 聊天参考\n\n私聊里的需求和讨论，以及群里值得对照的几句。启动不读。做事时按关键词查。\n',
            references,
        )
    os.makedirs(LEARN_ROOT, exist_ok=True)
    md_path = os.path.join(LEARN_ROOT, f'{day}.md')
    body = _render(day, buckets, actions, messages, history, opens, settled)
    if not dry_run:
        tmp = md_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(body)
        os.replace(tmp, md_path)
        _save_state(state)
        _touch_index(day, messages, buckets, new_n, up_n)

    return {
        'ok': True,
        'day': day,
        'messages': len(messages),
        'groups': len(_chat_counts(messages)),
        'chats': [{'title': title, 'n': n} for title, n in _chat_counts(messages)],
        'history': {
            'ok': bool(history.get('ok')),
            'error': history.get('error') or '',
            'groups': history.get('groups'),
            'privates': history.get('privates'),
            'scanned': history.get('scanned'),
            'written': history.get('written'),
        },
        'open_requirements': len(opens),
        'settled_metrics': len(settled),
        'noise': noise,
        'by_category': {k: len(v) for k, v in buckets.items()},
        'new_lessons': new_n,
        'upgraded': up_n,
        'digest': md_path if not dry_run else '',
        'actions': actions,
        'dry_run': dry_run,
    }


def _touch_index(day: str, messages: list[dict], buckets: dict, new_n: int, up_n: int) -> None:
    index = os.path.join(LEARN_ROOT, '_index.md')
    line = (
        f'| {day} | {len(messages)} | 新 {new_n} / 升级 {up_n} | '
        + '，'.join(f'{k}{len(v)}' for k, v in buckets.items() if k != '闲聊' and v)
        + f' | [{day}]({day}.md) |'
    )
    if not os.path.isfile(index):
        header = (
            '# 群聊日学习索引\n\n'
            '| 日期 | 消息 | 沉淀 | 分类 | 稿 |\n'
            '|------|------|------|------|----|\n'
        )
        with open(index, 'w', encoding='utf-8') as f:
            f.write(header + line + '\n')
        return
    text = open(index, encoding='utf-8').read()
    if f'| {day} |' in text:
        lines = []
        for raw in text.splitlines():
            lines.append(line if raw.startswith(f'| {day} |') else raw)
        with open(index, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return
    with open(index, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def _summary_text(result: dict) -> str:
    cats = result.get('by_category') or {}
    parts = [f'{k}{v}' for k, v in cats.items() if k != '闲聊' and v]
    actions = list(result.get('actions') or [])
    chats = list(result.get('chats') or [])
    history = result.get('history') or {}
    lines = [
        f"群聊学习 {result.get('day') or ''}",
        (
            f"读了 {result.get('messages', 0)} 条，来自 {result.get('groups', 0)} 个会话。"
            f"闲聊 {result.get('noise', 0)}。"
            f"新规矩 {result.get('new_lessons', 0)} 条，升级 {result.get('upgraded', 0)} 条。"
        ),
    ]
    if history.get('ok'):
        lines.append(
            f"回拉 {history.get('groups') or 0} 个群、{history.get('privates') or 0} 条私聊，"
            f"扫到 {history.get('scanned') or 0} 条。"
        )
    else:
        lines.append(f"回拉没完成：{history.get('error') or '未知'}。上面的条数不是全量。")
    if chats:
        lines.append('各群：')
        shown = chats[:30]
        lines.extend(f'· {row["title"]} {row["n"]}' for row in shown)
        if len(chats) > len(shown):
            lines.append(f'· 其余 {len(chats) - len(shown)} 个群在学习稿里')
    if parts:
        lines.append('分类：' + '，'.join(parts))
    if actions:
        lines.append('沉淀：')
        lines.extend(f'· {a}' for a in actions[:8])
        if len(actions) > 8:
            lines.append(f'· 其余 {len(actions) - 8} 条在学习稿里')
    else:
        lines.append('没有新规矩入库。')
    return '\n'.join(lines)[:3500]


def _owner_chat_id() -> int:
    if 8740305767 in ALLOWED_USERS:
        return 8740305767
    return ALLOWED_USERS[0] if ALLOWED_USERS else 0


def push_summary(result: dict) -> dict:
    """学完后的短汇总只发主人私聊。失败不回滚已写入的 lesson。"""
    chat_id = _owner_chat_id()
    if not TG_BOT_TOKEN or not chat_id:
        return {'ok': False, 'error': '缺少 token 或私聊对象'}
    body = json.dumps(
        {
            'chat_id': chat_id,
            'text': _summary_text(result),
            'disable_web_page_preview': True,
        },
        ensure_ascii=False,
    ).encode('utf-8')
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
        data=body,
        method='POST',
        headers={'Content-Type': 'application/json; charset=utf-8'},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {'ok': False, 'error': str(exc)}
    if not data.get('ok'):
        return {'ok': False, 'error': str(data)[:300]}
    return {'ok': True, 'chat_id': chat_id}


def main() -> int:
    parser = argparse.ArgumentParser(description='每日群聊分类学习并沉淀')
    parser.add_argument('--date', default='', help='YYYY-MM-DD，默认上海当天')
    parser.add_argument('--yesterday', action='store_true', help='处理上海昨天')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.date:
        day = args.date
    elif args.yesterday:
        day = (datetime.now(SHANGHAI) - timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        day = _today()
    result = learn_day(day, dry_run=args.dry_run)
    if not args.dry_run:
        result['tg'] = push_summary(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
