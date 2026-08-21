---
date: 2026-08-22
tags: [jike_checkin,tgbot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 关极客打卡改 .env 并延迟重启过签退窗；双机 tgbot 都要改，VPN/抽查不受影响

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

关极客打卡改 .env 并延迟重启过签退窗；双机 tgbot 都要改，VPN/抽查不受影响

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
