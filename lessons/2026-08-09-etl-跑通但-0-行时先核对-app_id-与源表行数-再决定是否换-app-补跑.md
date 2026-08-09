---
date: 2026-08-09
tags: [funnel-etl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ETL 跑通但 0 行时先核对 app_id 与源表行数，再决定是否换 app 补跑

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ETL 跑通但 0 行时先核对 app_id 与源表行数，再决定是否换 app 补跑

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
