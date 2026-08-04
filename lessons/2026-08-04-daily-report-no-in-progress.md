---
date: 2026-08-04
tags: [daily-report, writing-style, feedback]
severity: high
domain: ops
---

# 日报结果条禁止写「进行中」

## 背景

主人 2026-08-04 纠正：日报不要出现「进行中」。未完事项进死锁/明日，结果条只写当天已交付并标「已完成」。

## 正确做法

1. `【今日结果】`末尾只标 `已完成`
2. 未完 → `【死锁阻碍】` / `【明日动作】`
3. 正文禁止 `进行中` / `待确认`

## 关联

- feedback：`feedback_daily_report_no_in_progress.md`
- 规则：`.cursor/rules/daily-report.mdc`
