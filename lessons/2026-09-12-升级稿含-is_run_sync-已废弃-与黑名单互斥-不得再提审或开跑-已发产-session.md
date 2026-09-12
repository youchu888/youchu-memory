---
date: 2026-09-12
tags: [归因V1.0.11, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 升级稿含 is_run_sync 已废弃，与黑名单互斥，不得再提审或开跑；已发产 session 不回滚

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

升级稿含 is_run_sync 已废弃，与黑名单互斥，不得再提审或开跑；已发产 session 不回滚

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
