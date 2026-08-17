---
date: 2026-08-17
tags: [agent-bus,worker_ant,口径争议, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 狂人 bus 含 Q1/Q2/Q3 或「不许跳过三问」时禁止快车道 reply_only 结案，必须进主会话逐条填三问后再 reply

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

狂人 bus 含 Q1/Q2/Q3 或「不许跳过三问」时禁止快车道 reply_only 结案，必须进主会话逐条填三问后再 reply

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
