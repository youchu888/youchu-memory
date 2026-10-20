---
date: 2026-10-20
tags: [spark_migrate, session-rotate, self-evolve]
severity: medium
domain: ops
---

# dim|paimon|SR 维表无 dt 列时禁止抄 dim_app_info_all 的 dt 分区，改用 *_snap + snap_dt=${DT}，并对

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

dim|paimon|SR 维表无 dt 列时禁止抄 dim_app_info_all 的 dt 分区，改用 *_snap + snap_dt=${DT}，并对齐 844c4baf/_snap 样板

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
