---
date: 2026-11-12
tags: [etl,hourly,user_attr, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 小时挂用户属性仅用 `dwm_user_attr_intraday_d_d` dt=D；禁小时读 `dim_user_snap`

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

小时挂用户属性仅用 `dwm_user_attr_intraday_d_d` dt=D；禁小时读 `dim_user_snap`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
