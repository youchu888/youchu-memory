---
date: 2026-11-06
tags: [ctr-s7-prod-group, session-rotate, self-evolve]
severity: medium
domain: ops
---

# S4 上生产前从组内删除 dwd_app_pageitem_d_r，dim/ads 探针绑两张 dwd_r 的 partition；pb 正式表且 sr_use

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

S4 上生产前从组内删除 dwd_app_pageitem_d_r，dim/ads 探针绑两张 dwd_r 的 partition；pb 正式表且 sr_use_shadow=false，再 cascade S4 后重走 S7

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
