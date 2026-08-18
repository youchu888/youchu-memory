---
date: 2026-08-18
tags: [metric-library, session-rotate, self-evolve]
severity: medium
domain: ops
---

# MySQL 8 条件唯一用生成列 NULL 不参与 UNIQUE；`metric_label` 唯一键是 `(concept, kind, text)` + `

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

MySQL 8 条件唯一用生成列 NULL 不参与 UNIQUE；`metric_label` 唯一键是 `(concept, kind, text)` + `label_primary_slot`，不用 `canonical_code`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
