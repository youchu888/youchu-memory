---
date: 2026-08-25
tags: [cursor-session,metric-library,er-diagram, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 会话 resume 失败续做时，先查本地稿并对齐最新 spec 表名再推文档库，勿用旧临时名或旧版 spec 交差

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

会话 resume 失败续做时，先查本地稿并对齐最新 spec 表名再推文档库，勿用旧临时名或旧版 spec 交差

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
