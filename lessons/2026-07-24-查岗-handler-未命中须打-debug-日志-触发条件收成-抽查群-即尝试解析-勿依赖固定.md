---
date: 2026-07-24
tags: [attendance,tgbot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 查岗 handler 未命中须打 debug 日志，触发条件收成「抽查群 @ 即尝试解析」，勿依赖固定 marker 字符串

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

查岗 handler 未命中须打 debug 日志，触发条件收成「抽查群 @ 即尝试解析」，勿依赖固定 marker 字符串

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
