---
date: 2026-08-19
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 写/推日报前必须先跑双机 work-log 同步并读合并稿，禁止仅靠 transcript 在同步完成前定稿

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

写/推日报前必须先跑双机 work-log 同步并读合并稿，禁止仅靠 transcript 在同步完成前定稿

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
