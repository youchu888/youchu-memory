---
date: 2026-10-09
tags: [owner, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 问表/专项负责人时先查工作簿与需求 owner，再答；来源留存表 `dws.dws_source_analysis_retention_d` 当前负责人为野花

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

问表/专项负责人时先查工作簿与需求 owner，再答；来源留存表 `dws.dws_source_analysis_retention_d` 当前负责人为野花

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
