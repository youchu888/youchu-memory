---
date: 2026-10-23
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ACK 无可见回执时用 `agent_bus_send.py --no-dedup` 重发

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ACK 无可见回执时用 `agent_bus_send.py --no-dedup` 重发

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
