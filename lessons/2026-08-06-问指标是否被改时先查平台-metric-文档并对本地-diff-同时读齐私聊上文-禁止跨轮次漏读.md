---
date: 2026-08-06
tags: [context-continuity,platform-docs, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 问指标是否被改时先查平台 metric 文档并对本地 diff，同时读齐私聊上文，禁止跨轮次漏读 #263 类指令

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

问指标是否被改时先查平台 metric 文档并对本地 diff，同时读齐私聊上文，禁止跨轮次漏读 #263 类指令

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
