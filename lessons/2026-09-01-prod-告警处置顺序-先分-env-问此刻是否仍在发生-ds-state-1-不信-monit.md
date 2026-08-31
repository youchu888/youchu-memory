---
date: 2026-09-01
tags: [prod-monitor,oncall, session-rotate, self-evolve]
severity: medium
domain: ops
---

# prod 告警处置顺序：先分 env → 问此刻是否仍在发生（DS state=1，不信 monitor 快 1h 的时间戳）→ 追首个 FAILURE 真 t

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

prod 告警处置顺序：先分 env → 问此刻是否仍在发生（DS state=1，不信 monitor 快 1h 的时间戳）→ 追首个 FAILURE 真 task → download-log 取证，禁信根因字段与 DEPENDENT

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
