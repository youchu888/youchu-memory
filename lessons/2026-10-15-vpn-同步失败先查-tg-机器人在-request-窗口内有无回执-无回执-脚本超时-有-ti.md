---
date: 2026-10-15
tags: [vpn,tg-bot,ops, session-rotate, self-evolve]
severity: medium
domain: ops
---

# VPN 同步失败先查 TG 机器人在 `/request` 窗口内有无回执；无回执=脚本超时，有 `Timed out`=生成端超时，再选手动强制重导而非先修 

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

VPN 同步失败先查 TG 机器人在 `/request` 窗口内有无回执；无回执=脚本超时，有 `Timed out`=生成端超时，再选手动强制重导而非先修 OpenVPN

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
