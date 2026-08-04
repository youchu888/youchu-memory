---
date: 2026-08-04
tags: [daily-report, writing-style, dual-mac, tg, feedback]
severity: high
domain: ops
---

# 日报：只写已完成；死锁少写；未完进明日；推送仅 old-mac

## 背景

主人 2026-08-04 定稿：

- 不要「进行中」
- 今日结果只写已完成
- 死锁阻碍尽量不写
- 未完成列到明日动作
- 规则同步旧 Mac；自动推送由旧 Mac 做

## 正确做法

1. 双机 sync → 汇总 hosts → 只摘已完成写结果条
2. 未完 → `【明日动作】`；`【死锁阻碍】`默认空
3. old-mac 定稿并跑 `post_daily_report_to_dm.py`；new-mac 默认跳过推送

## 关联

- feedback：`feedback_daily_report_no_in_progress.md`
- playbook：`playbook_daily_weekly_report.md`
- 规则：`.cursor/rules/daily-report.mdc`
