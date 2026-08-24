---
date: 2026-08-24
tags: [dws, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 大漏斗|探表|答「有没有数」须分环境查 SR 行数与 prod 是否存在，Spark/Paimon 就绪≠ SR 可查

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

大漏斗|探表|答「有没有数」须分环境查 SR 行数与 prod 是否存在，Spark/Paimon 就绪≠ SR 可查

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
