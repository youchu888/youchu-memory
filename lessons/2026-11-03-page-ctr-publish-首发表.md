---
date: 2026-11-03
tags: [shadow-gate, session-rotate, self-evolve]
severity: medium
domain: ops
---

# page-ctr|publish|首发表

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

page-ctr|publish|首发表

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
