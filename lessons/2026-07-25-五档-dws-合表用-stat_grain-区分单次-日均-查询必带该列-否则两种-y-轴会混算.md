---
date: 2026-07-25
tags: [session_duration, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 五档 DWS 合表用 stat_grain 区分单次/日均，查询必带该列，否则两种 Y 轴会混算

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

五档 DWS 合表用 stat_grain 区分单次/日均，查询必带该列，否则两种 Y 轴会混算

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
