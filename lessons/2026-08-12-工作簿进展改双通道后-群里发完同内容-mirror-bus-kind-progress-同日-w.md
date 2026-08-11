---
date: 2026-08-12
tags: [workbook-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 工作簿进展改双通道后：群里发完同内容 mirror bus（kind=progress），同日 `workbook_progress_posted.json` 

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

工作簿进展改双通道后：群里发完同内容 mirror bus（kind=progress），同日 `workbook_progress_posted.json` 防重

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
