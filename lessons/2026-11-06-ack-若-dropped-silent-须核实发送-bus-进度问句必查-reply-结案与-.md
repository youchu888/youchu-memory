---
date: 2026-11-06
tags: [agent-bus-ack, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ACK 若 dropped:silent 须核实发送；bus 进度问句必查 reply 结案与 commit，并保证 60 秒内先 ack

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ACK 若 dropped:silent 须核实发送；bus 进度问句必查 reply 结案与 commit，并保证 60 秒内先 ack

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
