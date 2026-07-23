---
date: 2026-07-23
tags: [dolphin,datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 单 task 秒级 FAIL 且补跑成功：先跑验恢复四件套再判瞬时资源问题，不必改 SQL

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

单 task 秒级 FAIL 且补跑成功：先跑验恢复四件套再判瞬时资源问题，不必改 SQL

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
