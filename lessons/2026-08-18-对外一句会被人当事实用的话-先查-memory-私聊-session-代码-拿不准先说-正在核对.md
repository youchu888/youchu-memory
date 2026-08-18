---
date: 2026-08-18
tags: [agent-bus,workbook,口径, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 对外一句会被人当事实用的话，先查 memory/私聊/session/代码；拿不准先说「正在核对」，事项拆开写「已确认/未确认」

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

对外一句会被人当事实用的话，先查 memory/私聊/session/代码；拿不准先说「正在核对」，事项拆开写「已确认/未确认」

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
