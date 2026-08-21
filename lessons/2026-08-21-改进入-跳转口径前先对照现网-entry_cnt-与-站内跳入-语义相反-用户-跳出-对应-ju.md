---
date: 2026-08-21
tags: [page-visit,metric, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 改进入/跳转口径前先对照现网：`entry_cnt` 与「站内跳入」语义相反，用户「跳出」对应 `jump_cnt` 不是 `dropout_*`

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

改进入/跳转口径前先对照现网：`entry_cnt` 与「站内跳入」语义相反，用户「跳出」对应 `jump_cnt` 不是 `dropout_*`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
