---
date: 2026-10-20
tags: [datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# dim|prod SR 维表 0 行时 Paimon 空 snap_dt 分区先判源表是否真无数据，勿当同步逻辑故障

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

dim|prod SR 维表 0 行时 Paimon 空 snap_dt 分区先判源表是否真无数据，勿当同步逻辑故障

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
