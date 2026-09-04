---
date: 2026-09-04
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ACK 被 silent 丢时用 --no-dedup 重发，以 reply 成功为结案依据

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ACK 被 silent 丢时用 --no-dedup 重发，以 reply 成功为结案依据

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
