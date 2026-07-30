---
date: 2026-07-31
tags: [attribution, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 改时间分查 `dim_app_attribution_time_config`（无专属行即 default）；24h 窗口与套档逻辑在 ETL SQL，表改分 

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

改时间分查 `dim_app_attribution_time_config`（无专属行即 default）；24h 窗口与套档逻辑在 ETL SQL，表改分 T+1 生效

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
