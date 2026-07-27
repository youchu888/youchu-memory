---
date: 2026-07-27
tags: [tg-group, session-rotate, self-evolve]
severity: medium
domain: ops
---

# bus-reply|bus 派活要求「结论请回 bus」时，验完直接 agent-bus 结案，禁止再问主人是否发送

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

bus-reply|bus 派活要求「结论请回 bus」时，验完直接 agent-bus 结案，禁止再问主人是否发送

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
