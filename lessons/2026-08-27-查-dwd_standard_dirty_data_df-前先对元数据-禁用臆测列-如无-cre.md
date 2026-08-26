---
date: 2026-08-27
tags: [paimon,dirty_data,sql, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 查 `dwd_standard_dirty_data_df` 前先对元数据，禁用臆测列（如无 `create_time`）；注册事件用 `user_regist

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

查 `dwd_standard_dirty_data_df` 前先对元数据，禁用臆测列（如无 `create_time`）；注册事件用 `user_register`，勿混 `register`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
