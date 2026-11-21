---
date: 2026-11-21
tags: [ownership, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 活跃留存|问「是不是我们开发的」时先查 code_owners 与 Spark 索引，主链归知秋；又初勿默认认领 runner 迁库与 dws_app_*_d_

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

活跃留存|问「是不是我们开发的」时先查 code_owners 与 Spark 索引，主链归知秋；又初勿默认认领 runner 迁库与 dws_app_*_d_h 改动。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
