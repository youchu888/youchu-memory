---
date: 2026-07-29
tags: [device-tag,spark,ddl, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Paimon/Spark 表结构变更时用 DROP+CREATE bootstrap，禁止仅靠 CREATE TABLE IF NOT EXISTS 期望新列生

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Paimon/Spark 表结构变更时用 DROP+CREATE bootstrap，禁止仅靠 CREATE TABLE IF NOT EXISTS 期望新列生效

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
