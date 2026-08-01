---
date: 2026-08-01
tags: [datacheck,dws_session_duration_user_d, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 验用户停留时长：默认 T-1；查当月分区覆盖 + daily 无 bucket0 + session 0~5 + 与 dwm_app_session_sid_d

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

验用户停留时长：默认 T-1；查当月分区覆盖 + daily 无 bucket0 + session 0~5 + 与 dwm_app_session_sid_d 对 session_cnt

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
