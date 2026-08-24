---
date: 2026-08-24
tags: [metric-library-er, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 画 ER 时 v0.2 三层实线作底座，v0.3 entity/event/role 虚线标待拍板，避免未定方案被当成已定架构

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

画 ER 时 v0.2 三层实线作底座，v0.3 entity/event/role 虚线标待拍板，避免未定方案被当成已定架构

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
