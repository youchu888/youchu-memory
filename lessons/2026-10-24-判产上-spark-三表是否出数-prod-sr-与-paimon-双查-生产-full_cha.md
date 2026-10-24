---
date: 2026-10-24
tags: [datacheck,spark,promotion-summary, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 判产上 Spark 三表是否出数：prod SR 与 Paimon 双查 + 生产 full_chain 是否含任务；test/旧海豚有数不能替代产挂产

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

判产上 Spark 三表是否出数：prod SR 与 Paimon 双查 + 生产 full_chain 是否含任务；test/旧海豚有数不能替代产挂产

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
