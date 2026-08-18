---
date: 2026-08-18
tags: [metric-library, session-rotate, self-evolve]
severity: medium
domain: ops
---

# DDL 评审后改稿 push 不等于建表；Phase0 test DDL 须等 5 条拍板 + 知秋别名真源/lifecycle 两项，禁止抢跑

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

DDL 评审后改稿 push 不等于建表；Phase0 test DDL 须等 5 条拍板 + 知秋别名真源/lifecycle 两项，禁止抢跑

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
