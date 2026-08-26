---
date: 2026-08-27
tags: [dirty_data,datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 脏数据任务先 COUNT + COUNT(DISTINCT event_id) 验重复，再导明细；配合 `error_type/error_column` 与 

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

脏数据任务先 COUNT + COUNT(DISTINCT event_id) 验重复，再导明细；配合 `error_type/error_column` 与 `raw_data.payload.type` 归纳拦因

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
