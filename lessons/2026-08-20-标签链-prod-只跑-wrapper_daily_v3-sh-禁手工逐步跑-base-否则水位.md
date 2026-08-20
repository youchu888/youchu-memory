---
date: 2026-08-20
tags: [spark, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 标签链 prod 只跑 wrapper_daily_v3.sh，禁手工逐步跑 base，否则水位不提交会翻倍

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

标签链 prod 只跑 wrapper_daily_v3.sh，禁手工逐步跑 base，否则水位不提交会翻倍

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
