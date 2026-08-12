---
date: 2026-08-12
tags: [spark-cluster,deploy, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 开 YARN 前确认集群 spark 包与 origin/dev 一致，旧版单文件 SQL 与仓库两阶段 ETL 不同步会导致口径偏差

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

开 YARN 前确认集群 spark 包与 origin/dev 一致，旧版单文件 SQL 与仓库两阶段 ETL 不同步会导致口径偏差

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
