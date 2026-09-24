---
date: 2026-09-24
tags: [tg-bot,restart,vpn, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Telegram Bot 重启若 API 超时，先确认网络/VPN 与 API 可达，再用 daemon 拉起并手工验收，不单次脚本失败就停。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Telegram Bot 重启若 API 超时，先确认网络/VPN 与 API 可达，再用 daemon 拉起并手工验收，不单次脚本失败就停。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
