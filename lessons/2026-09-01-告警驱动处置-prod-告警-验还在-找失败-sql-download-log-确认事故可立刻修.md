---
date: 2026-09-01
tags: [prod-monitor, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 告警驱动处置：prod 告警→验还在→找失败 SQL→download-log；确认事故可立刻修，非事故变更等知秋 GO

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

告警驱动处置：prod 告警→验还在→找失败 SQL→download-log；确认事故可立刻修，非事故变更等知秋 GO

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
