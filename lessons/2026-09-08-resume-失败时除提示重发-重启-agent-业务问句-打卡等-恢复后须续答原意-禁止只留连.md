---
date: 2026-09-08
tags: [tg-cursor, session-rotate, self-evolve]
severity: medium
domain: ops
---

# resume 失败时除提示重发/重启 agent，业务问句（打卡等）恢复后须续答原意，禁止只留连接错误就结束

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

resume 失败时除提示重发/重启 agent，业务问句（打卡等）恢复后须续答原意，禁止只留连接错误就结束

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
