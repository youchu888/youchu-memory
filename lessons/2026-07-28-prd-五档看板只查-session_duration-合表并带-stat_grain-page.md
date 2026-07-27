---
date: 2026-07-28
tags: [session_duration,backend, session-rotate, self-evolve]
severity: medium
domain: ops
---

# PRD 五档看板只查 session_duration 合表并带 stat_grain；page_stay 的 valid_stay 与 session 墙钟不

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

PRD 五档看板只查 session_duration 合表并带 stat_grain；page_stay 的 valid_stay 与 session 墙钟不是同一指标

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
