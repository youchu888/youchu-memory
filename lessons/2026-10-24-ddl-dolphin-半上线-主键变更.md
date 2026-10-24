---
date: 2026-10-24
tags: [ads_dept_promotion_summary_m, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ddl|dolphin|半上线|主键变更

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ddl|dolphin|半上线|主键变更

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
