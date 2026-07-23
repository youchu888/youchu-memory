---
date: 2026-07-23
tags: [dolphin, session-rotate, self-evolve]
severity: medium
domain: ops
---

# get_task_instance_log 约 64KB 截断拿不到 SR 尾部错，需海豚 UI 翻页或 worker SSH 取完整 log

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

get_task_instance_log 约 64KB 截断拿不到 SR 尾部错，需海豚 UI 翻页或 worker SSH 取完整 log

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
