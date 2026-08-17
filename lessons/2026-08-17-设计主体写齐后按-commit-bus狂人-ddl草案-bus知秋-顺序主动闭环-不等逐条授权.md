---
date: 2026-08-17
tags: [design-delivery,agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 设计主体写齐后按 commit→bus狂人→DDL草案→bus知秋 顺序主动闭环，不等逐条授权

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

设计主体写齐后按 commit→bus狂人→DDL草案→bus知秋 顺序主动闭环，不等逐条授权

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
