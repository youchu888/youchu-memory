---
date: 2026-07-25
tags: [duration_model, session-rotate, self-evolve]
severity: medium
domain: ops
---

# page_stay 是 uid×dt 事实表，session_duration 是多维预聚合；合表只动后者，禁止与 page_stay 并表

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

page_stay 是 uid×dt 事实表，session_duration 是多维预聚合；合表只动后者，禁止与 page_stay 并表

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
