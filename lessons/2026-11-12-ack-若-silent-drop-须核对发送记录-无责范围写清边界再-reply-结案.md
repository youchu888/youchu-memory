---
date: 2026-11-12
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ACK 若 silent drop 须核对发送记录；无责范围写清边界再 reply 结案

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ACK 若 silent drop 须核对发送记录；无责范围写清边界再 reply 结案

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
