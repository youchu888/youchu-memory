---
date: 2026-08-17
tags: [lineage, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 血缘与现网不一致时以 prod 海豚 live task 为准；旧表停更须 deprecated 并为在跑新表重建血缘

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

血缘与现网不一致时以 prod 海豚 live task 为准；旧表停更须 deprecated 并为在跑新表重建血缘

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
