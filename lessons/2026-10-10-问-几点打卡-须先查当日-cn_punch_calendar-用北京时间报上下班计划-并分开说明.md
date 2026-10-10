---
date: 2026-10-10
tags: [punch,calendar, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 问「几点打卡」须先查当日 cn_punch_calendar，用北京时间报上下班计划，并分开说明「计划时刻」与「是否已成功打卡/调度是否会重试」。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

问「几点打卡」须先查当日 cn_punch_calendar，用北京时间报上下班计划，并分开说明「计划时刻」与「是否已成功打卡/调度是否会重试」。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
