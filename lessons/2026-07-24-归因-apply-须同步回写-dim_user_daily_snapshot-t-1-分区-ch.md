---
date: 2026-07-24
tags: [attribution,dim, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 归因 apply 须同步回写 `dim_user_daily_snapshot` T-1 分区 channel，与 all 表同口径；禁止单独重跑 result

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

归因 apply 须同步回写 `dim_user_daily_snapshot` T-1 分区 channel，与 all 表同口径；禁止单独重跑 result

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
