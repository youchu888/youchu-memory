---
date: 2026-08-12
tags: [big-funnel,datacheck,paimon, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 大漏斗集群读湖仓不读 SR，停跑自查优先查 Paimon 分区可读性与 Flink fanout schema，SR 正常不能作为可跑依据

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

大漏斗集群读湖仓不读 SR，停跑自查优先查 Paimon 分区可读性与 Flink fanout schema，SR 正常不能作为可跑依据

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
