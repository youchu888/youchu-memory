---
date: 2026-10-22
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 狂人声明「我直接做、不要再推」→ 停改停推、reply 说明已推 commit 与是否需回滚，勿继续跟该线 JDBC/SR 草稿。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

狂人声明「我直接做、不要再推」→ 停改停推、reply 说明已推 commit 与是否需回滚，勿继续跟该线 JDBC/SR 草稿。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
