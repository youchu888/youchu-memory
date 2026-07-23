---
date: 2026-07-24
tags: [tg-send,urllib,curl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# TG 群发 urllib 超时则 kill 进程并改用 curl 重发，成功后再报「已到达」

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

TG 群发 urllib 超时则 kill 进程并改用 curl 重发，成功后再报「已到达」

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
