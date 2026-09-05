#!/usr/bin/env python3
"""手动触发工作簿进展：T-1 实查后发一条（与 bot 自动逻辑一致）。"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import urllib.request
from pathlib import Path

TGBOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TGBOT_DIR))

from config import MONITOR_GROUP_CHAT_ID, TG_BOT_TOKEN, WORKER_ANT_BOT  # noqa: E402
from group_workbook_progress_handler import (  # noqa: E402
    fallback_workbook_template,
    post_workbook_pipeline,
    save_full_workbook_text,
    set_application,
    _workbook_date,
)
from workbook_progress_service import (  # noqa: E402
    _report_cutoff_date,
    build_progress_reply,
    fetch_live_snapshot,
)


class _FakeBot:
    def __init__(self, token: str):
        self.token = token

    async def send_message(self, *, chat_id: int, text: str, disable_web_page_preview: bool = True):
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        body = json.dumps(
            {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': disable_web_page_preview},
            ensure_ascii=False,
        ).encode()
        req = urllib.request.Request(
            url, data=body, method='POST', headers={'Content-Type': 'application/json; charset=utf-8'},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())


class _FakeApp:
    def __init__(self, token: str):
        self.bot = _FakeBot(token)


DEFAULT_WORKBOOK = fallback_workbook_template()


async def main() -> int:
    ap = argparse.ArgumentParser(description='Post workbook progress to monitor group')
    ap.add_argument('--dry-run', action='store_true', help='Print reply only (T-1 probe)')
    ap.add_argument('--file', help='Workbook text file')
    ap.add_argument(
        '--force-repost',
        action='store_true',
        help='Allow a second post for today (normally blocked)',
    )
    args = ap.parse_args()

    if args.file:
        workbook = Path(args.file).read_text(encoding='utf-8')
    else:
        workbook = DEFAULT_WORKBOOK
        if not args.dry_run:
            print('refuse: live group post requires --file (no canned fallback)', file=sys.stderr)
            return 2

    save_full_workbook_text(workbook)

    if args.dry_run:
        dt = _workbook_date(workbook)
        cutoff = _report_cutoff_date(dt)
        snap = fetch_live_snapshot(force=True, cutoff_dt=cutoff)
        print(f'=== workbook_date={dt} cutoff={cutoff} ===')
        print(build_progress_reply(workbook, snap=snap, workbook_date=dt))
        return 0

    app = _FakeApp(TG_BOT_TOKEN)
    set_application(app)
    ok = await post_workbook_pipeline(
        app,
        text=workbook,
        msg_id=0,
        source='manual_script',
        skip_if_date_done=not args.force_repost,
        force_repost=args.force_repost,
    )
    print('posted' if ok else 'skipped (already posted today or not workbook)')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
