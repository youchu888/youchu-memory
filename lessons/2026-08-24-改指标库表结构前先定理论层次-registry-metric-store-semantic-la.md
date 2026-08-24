---
date: 2026-08-24
tags: [metric-library-design, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 改指标库表结构前先定理论层次（Registry / Metric Store / Semantic Layer），对照业务约束选「Metric Store 为核

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

改指标库表结构前先定理论层次（Registry / Metric Store / Semantic Layer），对照业务约束选「Metric Store 为核的轻语义层」，勿默认纯登记表或全量 Ontology

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
