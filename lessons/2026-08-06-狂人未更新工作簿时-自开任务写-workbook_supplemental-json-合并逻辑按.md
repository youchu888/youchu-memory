---
date: 2026-08-06
tags: [workbook,task-tracking, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 狂人未更新工作簿时，自开任务写 workbook_supplemental.json，合并逻辑按编号/标题去重进每日汇报

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

狂人未更新工作簿时，自开任务写 workbook_supplemental.json，合并逻辑按编号/标题去重进每日汇报

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
