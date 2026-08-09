---
date: 2026-08-09
tags: [funnel-etl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 宽漏斗禁单 SQL 宽聚合，拆成 metrics + wide 两阶段，避免 driver heap OOM

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

宽漏斗禁单 SQL 宽聚合，拆成 metrics + wide 两阶段，避免 driver heap OOM

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
