---
date: 2026-10-16
tags: [daily-report, worklog, AUTHORITY_HOST]
severity: medium
domain: ops
---

# 正式日报不得写入双机汇总和权威主机

## 背景

2026-10-16 主人指出日报抬头又出现「双机汇总」「日报权威主机」。这两行会随定稿进 TG 和云端。

## 坑 / 错误做法

`worklog_dual_mac_sync.py` 的 `_stamp` 在「日期」后插入内部备注。权威机覆盖权靠 `AUTHORITY_HOST`，不靠日报正文。

## 正确做法

`_stamp` 只删除这两行，不再插入。正式稿抬头到「日期」为止。脚本两份都要改：`~/.dc-platform/scripts/worklog_dual_mac_sync.py` 与 `~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py`。

## 验证

`日报-2026-10-16.md` 与 `work-log/reports/2026-10-16-日报.md` 已无这两行。

## 关联

- 规则：`.cursor/rules/daily-report.mdc`
- 金样：`feedback_daily_report_golden_style_from_owner_edits.md`
