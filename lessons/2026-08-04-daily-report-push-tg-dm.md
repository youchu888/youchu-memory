---
date: 2026-08-04
tags: [tg, daily-report, dm, notify, old-mac]
severity: high
domain: ops
---

# 日报定稿后必须推送 TG 私聊（仅 old-mac）

## 背景

主人 2026-08-04：日报生成后推 Bot 私聊；**自动推送由旧 Mac 做**；规则经 memory 同步到旧机。

## 正确做法

1. old-mac 双机汇总后定稿
2. `python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py`
3. new-mac 默认 skip（非 authority）

## 关联

- canonical：`memory/scripts/post_daily_report_to_dm.py`
- feedback：`feedback_daily_report_push_tg_dm.md`
