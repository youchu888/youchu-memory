---
date: 2026-08-18
tags: [workbook,tgbot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 工作簿进展读当日 work-log 实活，禁捞旧 bus 挂账与每日重复模板；今天确认清楚再回，明天再报明天

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

工作簿进展读当日 work-log 实活，禁捞旧 bus 挂账与每日重复模板；今天确认清楚再回，明天再报明天

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
