---
date: 2026-09-18
tags: [datacheck,funnel,spark, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 大漏斗 prod 核查跳过海豚，改查 SR 分区行数、`update_time` 与 playbook 对照项

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

大漏斗 prod 核查跳过海豚，改查 SR 分区行数、`update_time` 与 playbook 对照项

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
