---
date: 2026-10-04
tags: [cursor-network, session-rotate, self-evolve]
severity: medium
domain: ops
---

# TG/Cursor 连续 ECONNRESET 或 API 不可达时，先排查 OpenVPN/代理路由，必要时关 VPN 再「重启 agent」并重发原指令

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

TG/Cursor 连续 ECONNRESET 或 API 不可达时，先排查 OpenVPN/代理路由，必要时关 VPN 再「重启 agent」并重发原指令

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
