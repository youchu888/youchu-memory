---
date: 2026-11-14
tags: [dolphin_prod, session-rotate, self-evolve]
severity: medium
domain: ops
---

# MCP publish 仅 test；prod 海豚 SQL 查 dolphin_ops/平台产发惯例，发前对 commit 与现网 diff + 安全窗口

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

MCP publish 仅 test；prod 海豚 SQL 查 dolphin_ops/平台产发惯例，发前对 commit 与现网 diff + 安全窗口

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
