---
date: 2026-08-11
tags: [daily-report, dual-mac, sync, tg]
severity: high
domain: ops
---

# 日报：先双机上传任务并同步，再写稿推 TG

## 主人原话对齐

每天新旧设备 21:30 前把当天任务上传 git → 互相同步 → 再整理日报 → 推 TG。

## 落地

- 21:20 `pre_daily_report_flush`（双机）
- 21:30 `daily-report-wake`（old-mac：再 sync → 唤醒写稿 → 推 TG）
