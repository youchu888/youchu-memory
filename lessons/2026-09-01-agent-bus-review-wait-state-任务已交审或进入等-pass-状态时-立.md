---
date: 2026-09-01
tags: [tg-progress, session-rotate, self-evolve]
severity: medium
domain: ops
---

# agent-bus-review|wait-state|任务已交审或进入等 PASS 状态时，立即取消所有定时进度提醒；仅在审结、打回或需拍板时再私聊通知

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

agent-bus-review|wait-state|任务已交审或进入等 PASS 状态时，立即取消所有定时进度提醒；仅在审结、打回或需拍板时再私聊通知

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
