---
date: 2026-08-16
tags: [status-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 未结项汇报必须二分「又初欠账」与「等外部拍板」，避免把 pending RP 说成又初完全没推进

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

未结项汇报必须二分「又初欠账」与「等外部拍板」，避免把 pending RP 说成又初完全没推进

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
