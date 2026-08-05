---
date: 2026-08-05
tags: [dev-session-stage, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 主人说「stage1-6 干完先不发」时：可标 stage done + test 跑通，但 **禁止** 擅自 commit/push/海豚 publish/

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

主人说「stage1-6 干完先不发」时：可标 stage done + test 跑通，但 **禁止** 擅自 commit/push/海豚 publish/request-publish

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
