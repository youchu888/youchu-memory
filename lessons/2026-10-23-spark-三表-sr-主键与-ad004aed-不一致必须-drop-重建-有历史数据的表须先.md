---
date: 2026-10-23
tags: [sr-ddl,mgmt-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Spark 三表 SR 主键与 ad004aed 不一致必须 DROP 重建；有历史数据的表须先确认清空后再让运维执行

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Spark 三表 SR 主键与 ad004aed 不一致必须 DROP 重建；有历史数据的表须先确认清空后再让运维执行

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
