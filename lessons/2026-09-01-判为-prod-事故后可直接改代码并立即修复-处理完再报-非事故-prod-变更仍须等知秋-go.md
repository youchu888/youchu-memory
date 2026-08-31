---
date: 2026-09-01
tags: [prod-incident,authorization, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 判为 prod 事故后可直接改代码并立即修复，处理完再报；非事故 prod 变更仍须等知秋 GO

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

判为 prod 事故后可直接改代码并立即修复，处理完再报；非事故 prod 变更仍须等知秋 GO

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
