---
date: 2026-08-21
tags: [datacheck,dolphin,dag, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 同工作流下游 SUCCESS 但字段全 NULL 时优先查任务依赖顺序与上游分区就绪时间，别误判为 SQL 逻辑错误

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

同工作流下游 SUCCESS 但字段全 NULL 时优先查任务依赖顺序与上游分区就绪时间，别误判为 SQL 逻辑错误

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
