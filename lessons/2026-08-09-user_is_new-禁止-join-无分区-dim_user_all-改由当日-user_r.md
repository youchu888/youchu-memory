---
date: 2026-08-09
tags: [funnel-etl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# user_is_new 禁止 JOIN 无分区 dim_user_all，改由当日 user_register 推导，避免 executor OOM

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

user_is_new 禁止 JOIN 无分区 dim_user_all，改由当日 user_register 推导，避免 executor OOM

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
