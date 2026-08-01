---
date: 2026-08-01
tags: [dev-session, session-rotate, self-evolve]
severity: medium
domain: ops
---

# session 被 admin 用 fix-metadata 摘表后，本地须同步改 task.yaml、文档口径，设备文件移 `_parked_*` 并为摘出范

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

session 被 admin 用 fix-metadata 摘表后，本地须同步改 task.yaml、文档口径，设备文件移 `_parked_*` 并为摘出范围新建独立 session，勿把已摘表推回 PUT `/full`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
