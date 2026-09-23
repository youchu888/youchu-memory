---
date: 2026-09-24
tags: [cursor-agent, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 连接失败丢弃 resume 时勿假设上下文还在，须冷启动记忆后重跑或让用户重发/新开 agent

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

连接失败丢弃 resume 时勿假设上下文还在，须冷启动记忆后重跑或让用户重发/新开 agent

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
