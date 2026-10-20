---
date: 2026-10-20
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ack|silent|no-dedup|ACK 可能被 silent 丢弃时用 --no-dedup 重发；结案与对账以 reply 为准，勿因 ACK 未镜像

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ack|silent|no-dedup|ACK 可能被 silent 丢弃时用 --no-dedup 重发；结案与对账以 reply 为准，勿因 ACK 未镜像而重复整单

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
