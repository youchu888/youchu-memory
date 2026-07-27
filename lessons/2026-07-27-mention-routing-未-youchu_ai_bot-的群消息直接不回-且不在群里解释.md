---
date: 2026-07-27
tags: [tg-group, session-rotate, self-evolve]
severity: medium
domain: ops
---

# mention-routing|未 @youchu_ai_bot 的群消息直接不回，且不在群里解释「为什么不回」

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

mention-routing|未 @youchu_ai_bot 的群消息直接不回，且不在群里解释「为什么不回」

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
