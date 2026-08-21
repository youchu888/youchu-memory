---
date: 2026-08-22
tags: [complement,ads, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 补跑前先核 SUCCESS PI 与上游；下游 NULL 先判上游是否本日无数，避免重复补跑

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

补跑前先核 SUCCESS PI 与上游；下游 NULL 先判上游是否本日无数，避免重复补跑

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
