---
date: 2026-11-25
tags: [daily-report,work-log, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 任意机上有交付就要先写 `.cursor/work-log/当日.md`，再指望 flush/sync；未写则同步只是空 hosts。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

任意机上有交付就要先写 `.cursor/work-log/当日.md`，再指望 flush/sync；未写则同步只是空 hosts。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
