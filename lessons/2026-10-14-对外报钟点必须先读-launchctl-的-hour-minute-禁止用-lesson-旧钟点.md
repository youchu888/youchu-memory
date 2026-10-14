---
date: 2026-10-14
tags: [定时回复, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 对外报钟点必须先读 launchctl 的 Hour/Minute，禁止用 lesson 旧钟点；与已定指令不一致时先改定时再按现网回复

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

对外报钟点必须先读 launchctl 的 Hour/Minute，禁止用 lesson 旧钟点；与已定指令不一致时先改定时再按现网回复

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
