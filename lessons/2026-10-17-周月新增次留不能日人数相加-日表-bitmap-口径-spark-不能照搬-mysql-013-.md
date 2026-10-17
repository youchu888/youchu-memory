---
date: 2026-10-17
tags: [spark迁移, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 周月新增次留不能日人数相加，日表 bitmap 口径 Spark 不能照搬 MySQL，013～018 等人数集合方案定稿再动

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

周月新增次留不能日人数相加，日表 bitmap 口径 Spark 不能照搬 MySQL，013～018 等人数集合方案定稿再动

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
