---
date: 2026-08-14
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# DAILY_REPORT 唤醒写入 wake_feed 但 executor 未消费时，补跑 sync→写稿→post_daily_report_to_dm.p

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

DAILY_REPORT 唤醒写入 wake_feed 但 executor 未消费时，补跑 sync→写稿→post_daily_report_to_dm.py 推 TG

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
