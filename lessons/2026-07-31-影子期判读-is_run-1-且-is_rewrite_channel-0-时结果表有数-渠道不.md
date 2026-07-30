---
date: 2026-07-31
tags: [attribution, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 影子期判读：`is_run=1` 且 `is_rewrite_channel=0` 时结果表有数、渠道不变、`rewrite_status` 为 NULL 均属

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

影子期判读：`is_run=1` 且 `is_rewrite_channel=0` 时结果表有数、渠道不变、`rewrite_status` 为 NULL 均属正常

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
