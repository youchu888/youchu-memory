---
date: 2026-11-14
tags: [蓝猫bot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# dc_cursor_bot 缺 cursor_shared_session 时不能代点 request-publish；产发卡点改会话持有人在平台重提申请

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

dc_cursor_bot 缺 cursor_shared_session 时不能代点 request-publish；产发卡点改会话持有人在平台重提申请

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
