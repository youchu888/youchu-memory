---
date: 2026-07-29
tags: [ops-system,templates,spark, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 新 Spark 任务 launcher 只填 JOB/SQL/PROFILE 走 _templates，wrapper 必须先 step0 DDL bootst

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

新 Spark 任务 launcher 只填 JOB/SQL/PROFILE 走 _templates，wrapper 必须先 step0 DDL bootstrap 再跑数

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
