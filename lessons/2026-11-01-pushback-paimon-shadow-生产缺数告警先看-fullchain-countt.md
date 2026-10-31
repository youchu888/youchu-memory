---
date: 2026-11-01
tags: [fullchain, session-rotate, self-evolve]
severity: medium
domain: ops
---

# pushback|paimon-shadow|生产缺数告警先看 fullchain countTable：paimonshadow=影子非真缺；真缺只看写正式表

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

pushback|paimon-shadow|生产缺数告警先看 fullchain countTable：paimonshadow=影子非真缺；真缺只看写正式表的步

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
