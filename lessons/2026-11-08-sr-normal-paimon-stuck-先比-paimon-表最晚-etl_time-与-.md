---
date: 2026-11-08
tags: [paimon, session-rotate, self-evolve]
severity: medium
domain: ops
---

# SR-normal-Paimon-stuck|先比 Paimon 表最晚 etl_time 与 SR 结算等同窗水位；SR 在写、Paimon 不动则升级 Fa

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

SR-normal-Paimon-stuck|先比 Paimon 表最晚 etl_time 与 SR 结算等同窗水位；SR 在写、Paimon 不动则升级 Fanout/Flink（@斯科特），勿在下游盲补

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
