---
date: 2026-09-03
tags: [cursor-vpn, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 换 VPN 后会话 resume 易断，连接失败时让用户「重启 agent」并接上上一轮任务续做

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

换 VPN 后会话 resume 易断，连接失败时让用户「重启 agent」并接上上一轮任务续做

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
