---
date: 2026-09-04
tags: [大漏斗, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 摘 new 改 stage_metrics 时 _h_r 天计次固定 COUNT(DISTINCT event_id)，legacy daily.sql 用 t

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

摘 new 改 stage_metrics 时 _h_r 天计次固定 COUNT(DISTINCT event_id)，legacy daily.sql 用 task.yaml disabled 冻结勿删

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
