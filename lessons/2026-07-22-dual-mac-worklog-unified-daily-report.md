---
date: 2026-07-22
tags: [daily-report, work-log, dual-mac, sync, feedback]
severity: high
domain: ops
---

# 双 Mac 任务流水统一后再写日报

## 背景

主人 07-22 指出：新 Mac 与旧 Mac 整理的日报不一样。根因是 transcript / `.cursor/work-log` 只在本机，记忆 Git 原先不同步 work-log。

## 正确做法

1. 各机设 `WORKLOG_HOST_ID`（`new-mac` / `old-mac`）于 `~/.dc-platform/memory/.env.host`
2. 收尾写本机 `CHcode/.cursor/work-log/`
3. `worklog_dual_mac_sync.py` → `hosts/<id>/` + 合并 `YYYY-MM-DD.md`
4. `sync-memory-git.sh` 自动带上上述步骤
5. 写日报只认合并稿 + `work-log/reports/` 权威稿

## 关联

- `work-log/README.md`
- `scripts/worklog_dual_mac_sync.py`
- `playbook_daily_weekly_report.md`
- `feedback_work_log_multi_agent_reports.md`
