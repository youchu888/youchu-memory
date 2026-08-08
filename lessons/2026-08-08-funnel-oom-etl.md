---
date: 2026-08-08
tags: [spark, session-rotate, self-evolve]
severity: medium
domain: ops
---

# funnel|oom|etl

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

funnel|oom|etl

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
