"""工作簿进展：先查 T-1（汇报日前一日）实数 + work-log，再发**一条**群进展。

铁律（主人 2026-09-03）：
- 禁止精简秒回 / 双条 follow-up
- 口径 = 截至工作簿日 D 的 cutoff=D-1；当天实活不进当天群进展
- 正文必须带 T-1 探针数字 + cutoff 日 work-log 近况；禁止日复一日同一套话
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from config import PROJECT_ROOT, TGBOT_DIR, WORKER_ANT_BOT

_BJ = ZoneInfo('Asia/Shanghai')
_PROD_CNF = Path(PROJECT_ROOT) / '.claude' / 'database' / 'my.cnf.prod'
_TEST_CNF = Path(PROJECT_ROOT) / '.claude' / 'database' / 'my.cnf.test'
_CACHE_PATH = Path(TGBOT_DIR) / 'data' / 'workbook_live_cache.json'
_SUPPLEMENTAL_PATH = Path(TGBOT_DIR) / 'data' / 'workbook_supplemental.json'
_TASK_BOARD = Path.home() / '.dc-platform' / 'memory' / 'project_youchu_workbook_tasks.md'
_MEMORY_WORKLOG = Path.home() / '.dc-platform' / 'memory' / 'work-log'
_LOCAL_WORKLOG = Path(PROJECT_ROOT) / '.cursor' / 'work-log'
_CACHE_TTL_SEC = 90


@dataclass
class LiveSnapshot:
    ts: str = ''
    cutoff_dt: str = ''
    page_visit_rows: int = 0
    page_visit_pv: int = 0
    page_visit_entry: int = 0
    page_visit_jump: int = 0
    page_visit_dropout: int = 0
    page_visit_ok: bool = False
    page_stay_rows: int = 0
    result_rows: int = 0
    result_success: int = 0
    result_ok: bool = False
    result_max_dt: str = ''
    device_tag_max_dt: str = ''
    device_tag_rows: int = 0
    device_tag_prod: str = '未上线'
    notes: list[str] = field(default_factory=list)


def _report_cutoff_date(workbook_date: str) -> str:
    """汇报日 D → 口径截止日 D-1。"""
    try:
        d = datetime.strptime(workbook_date[:10], '%Y-%m-%d')
    except ValueError:
        d = datetime.now(_BJ)
    return (d - timedelta(days=1)).strftime('%Y-%m-%d')


def _mysql_row(cnf: Path, sql: str) -> list[str]:
    if not cnf.is_file():
        return []
    try:
        out = subprocess.run(
            ['mysql', f'--defaults-extra-file={cnf}', '-N', '-e', sql],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if out.returncode != 0 or not out.stdout.strip():
            return []
        return out.stdout.strip().split('\t')
    except (OSError, subprocess.TimeoutExpired):
        return []


def fetch_live_snapshot(*, force: bool = False, cutoff_dt: str | None = None) -> LiveSnapshot:
    now = datetime.now(_BJ)
    cutoff = cutoff_dt or (now - timedelta(days=1)).strftime('%Y-%m-%d')

    if not force and _CACHE_PATH.is_file():
        try:
            cached = json.loads(_CACHE_PATH.read_text(encoding='utf-8'))
            age = (now - datetime.fromisoformat(cached['ts'])).total_seconds()
            if age < _CACHE_TTL_SEC and cached.get('cutoff_dt') == cutoff:
                snap = LiveSnapshot(**{
                    k: cached[k]
                    for k in LiveSnapshot.__dataclass_fields__
                    if k in cached
                })
                snap.notes = list(cached.get('notes') or [])
                return snap
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    snap = LiveSnapshot(ts=now.strftime('%Y-%m-%d %H:%M:%S'), cutoff_dt=cutoff)

    pv = _mysql_row(
        _PROD_CNF,
        f"SELECT COUNT(*), IFNULL(SUM(pv_cnt),0), IFNULL(SUM(entry_cnt),0), "
        f"IFNULL(SUM(jump_cnt),0), IFNULL(SUM(dropout_page_cnt),0) "
        f"FROM dws.dws_app_page_visit_d_d WHERE dt='{cutoff}'",
    )
    if len(pv) >= 5:
        snap.page_visit_rows = int(float(pv[0] or 0))
        snap.page_visit_pv = int(float(pv[1] or 0))
        snap.page_visit_entry = int(float(pv[2] or 0))
        snap.page_visit_jump = int(float(pv[3] or 0))
        snap.page_visit_dropout = int(float(pv[4] or 0))
        snap.page_visit_ok = snap.page_visit_rows > 0
    else:
        snap.notes.append(f'page_visit dt={cutoff} 读不到分区')

    stay = _mysql_row(
        _PROD_CNF,
        f"SELECT COUNT(*) FROM dwd.dwd_app_page_stay_d WHERE dt='{cutoff}'",
    )
    if stay:
        snap.page_stay_rows = int(float(stay[0] or 0))

    max_dt = (_mysql_row(_PROD_CNF, 'SELECT MAX(dt) FROM dws.dws_register_attribution_result_d') or [''])[0]
    snap.result_max_dt = max_dt or '—'
    res = _mysql_row(
        _PROD_CNF,
        f"SELECT COUNT(*), IFNULL(SUM(attribution_status='success'),0) "
        f"FROM dws.dws_register_attribution_result_d WHERE dt='{cutoff}'",
    )
    if len(res) >= 2:
        snap.result_rows = int(float(res[0] or 0))
        snap.result_success = int(float(res[1] or 0))
        snap.result_ok = snap.result_rows > 0
    else:
        snap.notes.append(f'result_d dt={cutoff} 读不到分区')

    dev = _mysql_row(
        _TEST_CNF,
        'SELECT MAX(calc_dt), COUNT(*) FROM dws.dws_device_tag_d '
        'WHERE calc_dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)',
    )
    if len(dev) >= 2:
        snap.device_tag_max_dt = dev[0] or '—'
        snap.device_tag_rows = int(float(dev[1] or 0))

    prod_dev = _mysql_row(
        _PROD_CNF,
        'SELECT COUNT(*) FROM information_schema.tables '
        "WHERE table_schema='dws' AND table_name='dws_device_tag_d'",
    )
    snap.device_tag_prod = '未上线' if not prod_dev or int(float(prod_dev[0] or 0)) == 0 else '已建表'

    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {**snap.__dict__, 'notes': snap.notes}
        _CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    except OSError:
        pass
    return snap


def load_supplemental_items() -> list[dict]:
    """自开/增补项：必须读 JSON，禁止硬编码标题。"""
    if not _SUPPLEMENTAL_PATH.is_file():
        return []
    try:
        data = json.loads(_SUPPLEMENTAL_PATH.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return []
    items = data.get('items') if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    out: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = (it.get('title') or '').strip()
        if not title:
            continue
        out.append({
            'no': it.get('no') or it.get('id') or '补',
            'title': title,
            'assignee': it.get('assignee') or '又初',
            'status': (it.get('status') or '').strip(),
            'note': (it.get('note') or it.get('progress') or '').strip(),
            'source': 'supplemental',
        })
    return out


def _task_board_notes() -> dict[str, str]:
    """从权威 task 板抽「任务关键字 → 截至汇报前状态句」。"""
    if not _TASK_BOARD.is_file():
        return {}
    try:
        text = _TASK_BOARD.read_text(encoding='utf-8')
    except OSError:
        return {}
    notes: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 3:
            continue
        if cells[0] in {'#', '代号', '---'} or set(cells[0]) <= {'-'}:
            continue
        title = cells[1] if not cells[1].isdigit() else (cells[1] if len(cells) < 4 else cells[1])
        # 表格式：#|任务|状态|截至… 或 代号|任务|状态|截至…
        if len(cells) >= 4 and cells[0] not in {'任务'}:
            title = cells[1]
            status = cells[2]
            cutoff_note = cells[3]
        elif len(cells) >= 3:
            title = cells[0]
            status = cells[1]
            cutoff_note = cells[2]
        else:
            continue
        if title in {'任务', '---'} or status in {'状态'}:
            continue
        key = title[:40]
        notes[key] = f'{status} · {cutoff_note}'.strip(' ·')
    return notes


def _worklog_snippets(cutoff_dt: str, *, limit: int = 6) -> list[str]:
    """读 cutoff 日 work-log 近况；跳过 bus 长表噪音。"""
    candidates = [
        _LOCAL_WORKLOG / f'{cutoff_dt}.md',
        _MEMORY_WORKLOG / f'{cutoff_dt}.md',
        _MEMORY_WORKLOG / 'hosts' / 'new-mac' / f'{cutoff_dt}.md',
        _MEMORY_WORKLOG / 'hosts' / 'old-mac' / f'{cutoff_dt}.md',
    ]
    raw = ''
    for p in candidates:
        if p.is_file():
            try:
                raw = p.read_text(encoding='utf-8')
                if '已完成' in raw or '实活' in raw or '进展' in raw:
                    break
            except OSError:
                continue
    if not raw:
        return []

    snippets: list[str] = []
    # 优先抓「## 已完成 / 进展」下非空短行
    m = re.search(r'##\s*已完成[^\n]*\n([\s\S]*?)(?:\n##\s|\Z)', raw)
    block = m.group(1) if m else raw
    for line in block.splitlines():
        s = line.strip()
        if not s or s.startswith('#') or s.startswith('>') or s.startswith('|'):
            continue
        if 'ops-mirror' in s or 'bus#' in s.lower() or '未结案' in s:
            continue
        if s.startswith('（来源') or s.startswith('_'):
            continue
        if len(s) < 4:
            continue
        snippets.append(s[:160])
        if len(snippets) >= limit:
            break

    # 再从 task 板「当日实活」区兜底（若 cutoff 文件太空）
    if len(snippets) < 2 and _TASK_BOARD.is_file():
        try:
            board = _TASK_BOARD.read_text(encoding='utf-8')
        except OSError:
            board = ''
        for line in board.splitlines():
            if cutoff_dt[:7] not in line and '实活' not in line:
                # 仍允许抓含 commit / PASS / published 的短行
                pass
            if not line.startswith('|'):
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) < 4:
                continue
            if cells[0] in {'代号', '#'} or set(cells[0]) <= {'-'}:
                continue
            note = cells[-1]
            if any(k in note for k in ('push', 'PASS', 'published', '交审', '补数', '分区', 'SHA', '`')):
                snippets.append(f"{cells[1]}：{note[:140]}")
            if len(snippets) >= limit:
                break
    return snippets[:limit]


def _match_board_note(title: str, board: dict[str, str]) -> str:
    for k, v in board.items():
        if not k:
            continue
        if k in title or title in k:
            return v
        # 关键字重叠
        keys = re.findall(r'[\u4e00-\u9fffA-Za-z0-9_]{2,}', k)
        if keys and sum(1 for x in keys if x in title) >= max(1, len(keys) // 2):
            return v
    return ''


def _fmt_n(n: int) -> str:
    if n >= 100_000_000:
        return f'{n / 100_000_000:.2f} 亿'
    if n >= 10_000:
        return f'{n / 10_000:.1f} 万'
    return str(n)


def _progress_page(title: str, s: LiveSnapshot, board_note: str, wl: list[str]) -> tuple[str, str]:
    if not s.page_visit_ok:
        st = '异常'
        note = f"prod `dws_app_page_visit_d_d` **dt={s.cutoff_dt}** 无分区/0 行"
    else:
        st = '维护中'
        note = (
            f"prod 页面访问 **dt={s.cutoff_dt}**："
            f"{s.page_visit_rows} 行 · pv {_fmt_n(s.page_visit_pv)} · "
            f"进入 {_fmt_n(s.page_visit_entry)} · 跳转 {_fmt_n(s.page_visit_jump)} · "
            f"跳出页次 {_fmt_n(s.page_visit_dropout)}"
        )
        if s.page_stay_rows:
            note += f"；停留明细 `{s.cutoff_dt}` {_fmt_n(s.page_stay_rows)} 行"
    if board_note:
        note += f"；任务板：{board_note}"
    hit = [x for x in wl if re.search(r'页面|访问|停留|分区', x)]
    if hit:
        note += f"；近况：{'；'.join(hit[:2])}"
    return st, note


def _progress_attribution(title: str, s: LiveSnapshot, board_note: str, wl: list[str]) -> tuple[str, str]:
    if not s.result_ok:
        st = '异常'
        note = (
            f"prod `result_d` **dt={s.cutoff_dt}** 无数据"
            f"（表 max_dt={s.result_max_dt or '—'}）"
        )
    else:
        st = '维护中'
        rate = (100.0 * s.result_success / s.result_rows) if s.result_rows else 0.0
        note = (
            f"prod 归因 result_d **dt={s.cutoff_dt}**："
            f"{s.result_rows} 行 / success {s.result_success}（{rate:.1f}%）"
        )
    if board_note:
        note += f"；任务板：{board_note}"
    hit = [x for x in wl if re.search(r'归因|渠道|影子|result', x)]
    if hit:
        note += f"；近况：{'；'.join(hit[:2])}"
    return st, note


def _progress_generic(title: str, s: LiveSnapshot, board_note: str, item: dict, wl: list[str]) -> tuple[str, str]:
    st = (item.get('status') or board_note.split('·')[0].strip() or '进行中').strip() or '进行中'
    parts: list[str] = []
    if item.get('note'):
        parts.append(item['note'])
    if board_note:
        parts.append(f'任务板：{board_note}')
    hit = [x for x in wl if any(k in x for k in re.findall(r'[\u4e00-\u9fffA-Za-z0-9_]{2,}', title)[:4])]
    if hit:
        parts.append('近况：' + '；'.join(hit[:2]))
    if not parts:
        parts.append(f'口径截至 {s.cutoff_dt}；无独立探针，已读 task 板/work-log')
    return st, '；'.join(parts)


def _classify(title: str) -> str:
    if re.search(r'页面|访问|停留|进入|跳转|跳出', title):
        return 'page'
    if re.search(r'归因|渠道|影子', title):
        return 'attr'
    return 'other'


def build_progress_reply(
    text: str,
    *,
    snap: LiveSnapshot | None = None,
    workbook_date: str | None = None,
) -> str | None:
    """唯一群进展正文：T-1 实查后再拼，无「精简秒回」。"""
    from group_workbook_progress_handler import parse_youchu_items, _workbook_date

    dt = workbook_date or _workbook_date(text)
    cutoff = _report_cutoff_date(dt)
    s = snap or fetch_live_snapshot(force=True, cutoff_dt=cutoff)
    if s.cutoff_dt != cutoff:
        s = fetch_live_snapshot(force=True, cutoff_dt=cutoff)

    items = parse_youchu_items(text)
    # 簿里没有又初项时，仍报 task 板主责 + supplemental（避免复读默认 3/4 旧标题）
    if not items:
        board = _TASK_BOARD.read_text(encoding='utf-8') if _TASK_BOARD.is_file() else ''
        for i, line in enumerate(board.splitlines(), 1):
            m = re.search(r'^\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|', line)
            if m and '又初' not in line:
                # 主责表不一定含「又初」字样；团队簿区默认又初
                pass
            m2 = re.search(r'^\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|', line)
            if m2 and m2.group(1).isdigit():
                title = m2.group(2).strip()
                if title in {'任务'} or set(title) <= {'-'}:
                    continue
                if any(k in title for k in ('页面', '归因', '渠道', '标签', '漏斗', '指标')):
                    items.append({
                        'no': int(m2.group(1)),
                        'title': title,
                        'assignee': '又初',
                        'status': m2.group(3).strip(),
                        'note': m2.group(4).strip(),
                        'source': 'task_board',
                    })
        items = items[:6]

    supp = load_supplemental_items()
    seen_titles = {it['title'] for it in items}
    for it in supp:
        if it['title'] not in seen_titles:
            items.append(it)
            seen_titles.add(it['title'])

    if not items:
        return None

    board_notes = _task_board_notes()
    wl = _worklog_snippets(cutoff)
    ant = WORKER_ANT_BOT.lstrip('@')

    lines = [
        f'@{ant}',
        '',
        f'又初 · 工作簿 {dt} 进展（实查 · 口径截至 {cutoff}）',
        f'探针时间 {s.ts} CST · 禁止秒回模板',
        '',
    ]
    if s.notes:
        lines.append('探针告警：' + '；'.join(s.notes))
        lines.append('')

    for it in items:
        title = it['title']
        board_note = _match_board_note(title, board_notes) or (it.get('note') or '')
        kind = _classify(title)
        if kind == 'page':
            st, note = _progress_page(title, s, board_note, wl)
        elif kind == 'attr':
            st, note = _progress_attribution(title, s, board_note, wl)
        else:
            st, note = _progress_generic(title, s, board_note, it, wl)
        lines.extend([
            f"{it['no']}）{title}",
            f'状态：{st}',
            f'进展：{note}',
            '',
        ])

    if wl and not any('近况：' in (ln or '') for ln in lines):
        lines.append('cutoff 近况：' + '；'.join(wl[:3]))
        lines.append('')

    lines.append('— 又初')
    return '\n'.join(lines).strip()


# ---- 兼容旧调用名（一律走单条实查，不再秒回） ----

def build_brief_reply(
    text: str,
    *,
    snap: LiveSnapshot | None = None,
    expect_detailed_followup: bool = False,  # noqa: ARG001 — 废弃，保留签名
) -> str | None:
    return build_progress_reply(text, snap=snap)


def build_detailed_reply(text: str, *, snap: LiveSnapshot | None = None) -> str | None:
    """已废弃双条详细版；返回 None，避免再发第二条。"""
    return None


def split_for_telegram(text: str, *, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    buf = ''
    for line in text.splitlines(keepends=True):
        if len(buf) + len(line) > limit and buf:
            parts.append(buf.rstrip())
            buf = line
        else:
            buf += line
    if buf.strip():
        parts.append(buf.rstrip())
    return parts or [text[:limit]]
