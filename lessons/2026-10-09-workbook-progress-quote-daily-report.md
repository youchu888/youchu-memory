---
date: 2026-10-09
tags: [workbook, progress, daily-report]
severity: high
domain: ops
---

# 工作簿进展照抄 cutoff 日日报，禁止「任务板仅挂账」套话

## 背景

2026-10-09 09:00 工作簿进展把指标库、渠道周月写成「未查到探针数字，任务板仅挂账进行中」。当天日报已写渠道周月核对、交建表、提审。

## 坑 / 错误做法

1. `_worklog_snippets` 读到本机 work-log 里空的「已完成」占位就停，没读 memory 合并稿里的【今日结果】。
2. 对不上固定三张表探针的项，一律输出「不套模板；任务板仅挂账」。
3. 剥掉 `[TQ-002 | 渠道报表]` 后再做关键词匹配，「核对周报」对不上「渠道」。

## 正确做法

`workbook_progress_service.py`：取 cutoff 日【今日结果】最全的一份；匹配时保留方括号里的任务名，展示时去掉。原句写了已完成才标已完成。日报没有的项，引用 `MEMORY_OPEN.md` 里带更新日期的原句。禁止「无当日记录 / 等审核 / 维护中 / 任务板仅挂账」。改完重启 `omdb/tgbot/restart.sh`。

## 验证

用 `data/workbook_live_cache.json` + `workbook_last_full.json` 本地拼 2026-10-09 正文：渠道三条原句都在，正文无「任务板仅挂账」。

## 关联

- `omdb/tgbot/workbook_progress_service.py`
- `feedback_workbook_progress_list_plus_owned_cutoff.md`
