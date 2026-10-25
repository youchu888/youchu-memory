---
date: 2026-10-25
tags: [datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 汇报 pipeline 挂账写清卡点日期格、pending_count、block_reason 上游表，并区分探针等待与卡死（>20min 同一步无进展）

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

汇报 pipeline 挂账写清卡点日期格、pending_count、block_reason 上游表，并区分探针等待与卡死（>20min 同一步无进展）

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
