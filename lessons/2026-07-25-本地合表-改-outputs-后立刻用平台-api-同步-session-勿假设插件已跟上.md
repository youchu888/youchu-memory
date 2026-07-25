---
date: 2026-07-25
tags: [dev-session, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 本地合表/改 outputs 后立刻用平台 API 同步 session，勿假设插件已跟上

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

本地合表/改 outputs 后立刻用平台 API 同步 session，勿假设插件已跟上

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
