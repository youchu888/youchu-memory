---
date: 2026-07-29
tags: [device-tag,dolphin,merge-pool, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 姿态 F 主链路不经过 merge_pool；海豚老 task P0 与 Spark 迁移方向一致时不修 SQL，等 F 跑通后整 wf 下线

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

姿态 F 主链路不经过 merge_pool；海豚老 task P0 与 Spark 迁移方向一致时不修 SQL，等 F 跑通后整 wf 下线

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
