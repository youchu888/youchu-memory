---
date: 2026-08-01
tags: [dev-session,request-publish, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 改链路审核人时扫同链路全部 pending RP；approved 旧 session 不自动跟随，prod 发版换人须单开处理

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

改链路审核人时扫同链路全部 pending RP；approved 旧 session 不自动跟随，prod 发版换人须单开处理

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
