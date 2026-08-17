---
date: 2026-08-17
tags: [session_duration,bounce,datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# prod 有分区有数不能证明口径对；bounce 争议看 DWM is_bounce 与 DWS bucket0/bounce_cnt 是否对齐，未拍板前标 H

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

prod 有分区有数不能证明口径对；bounce 争议看 DWM is_bounce 与 DWS bucket0/bounce_cnt 是否对齐，未拍板前标 HOLD、禁 45 天 prod 重跑

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
