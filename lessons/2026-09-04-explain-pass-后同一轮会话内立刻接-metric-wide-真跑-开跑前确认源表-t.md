---
date: 2026-09-04
tags: [funnel, session-rotate, self-evolve]
severity: medium
domain: ops
---

# explain PASS 后同一轮会话内立刻接 metric→wide 真跑，开跑前确认源表 T-1 分区有数且 `--dt` 任务日与业务日对齐

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

explain PASS 后同一轮会话内立刻接 metric→wide 真跑，开跑前确认源表 T-1 分区有数且 `--dt` 任务日与业务日对齐

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
