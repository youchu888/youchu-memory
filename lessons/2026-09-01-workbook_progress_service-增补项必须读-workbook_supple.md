---
date: 2026-09-01
tags: [workbook, session-rotate, self-evolve]
severity: medium
domain: ops
---

# workbook_progress_service 增补项必须读 workbook_supplemental.json，禁止 _local_tracking_i

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

workbook_progress_service 增补项必须读 workbook_supplemental.json，禁止 _local_tracking_items 硬编码

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
