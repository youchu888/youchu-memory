---
date: 2026-08-10
tags: [etl-validation,funnel, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 大漏斗扩全量前先用 SF-81 按 playbook 做口径 spot-check，宽表 is_new 三档各 1 行 + stg 行数对齐后再排 M 压测

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

大漏斗扩全量前先用 SF-81 按 playbook 做口径 spot-check，宽表 is_new 三档各 1 行 + stg 行数对齐后再排 M 压测

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
