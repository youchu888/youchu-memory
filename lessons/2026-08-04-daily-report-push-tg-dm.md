---
date: 2026-08-04
tags: [tg, daily-report, dm, notify]
severity: high
domain: ops
---

# 日报定稿后必须推送 TG 私聊

## 背景

主人 2026-08-04 要求：每天 21:30（口语「九点半」）日报生成后，推送到又初 Bot 私聊，不能只停在 Cursor。

## 正确做法

1. 按 `daily-report.mdc` 生成并落盘（双机多 Agent 先同步再汇总）
2. 跑：`omdb/tgbot/.venv/bin/python omdb/tgbot/scripts/post_daily_report_to_dm.py`
3. 同日已推过默认跳过；`--force` 重发
4. 结果条末尾只标「已完成」，禁止「进行中」

## 关联

- 脚本：`omdb/tgbot/scripts/post_daily_report_to_dm.py`
- feedback：`feedback_daily_report_push_tg_dm.md` / `feedback_daily_report_no_in_progress.md`
