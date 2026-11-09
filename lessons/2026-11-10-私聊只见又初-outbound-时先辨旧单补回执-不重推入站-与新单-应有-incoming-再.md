---
date: 2026-11-10
tags: [tg-mirror,agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 私聊只见又初 outbound 时先辨旧单补回执（不重推入站）与新单（应有 🐜 incoming），再对 bus 日志。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

私聊只见又初 outbound 时先辨旧单补回执（不重推入站）与新单（应有 🐜 incoming），再对 bus 日志。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
