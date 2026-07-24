---
date: 2026-07-24
tags: [agent-bus,tg, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 跨 Agent 分工对齐走 bus 互督 checkpoint，不在群里公开回复派活细节

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

跨 Agent 分工对齐走 bus 互督 checkpoint，不在群里公开回复派活细节

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
