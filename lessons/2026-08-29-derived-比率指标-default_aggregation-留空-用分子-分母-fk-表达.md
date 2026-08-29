---
date: 2026-08-29
tags: [指标库G2, session-rotate, self-evolve]
severity: medium
domain: ops
---

# derived 比率指标：`default_aggregation` 留空，用分子/分母 FK 表达；`ratio` 不算白名单 agg

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

derived 比率指标：`default_aggregation` 留空，用分子/分母 FK 表达；`ratio` 不算白名单 agg

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
