---
date: 2026-10-30
tags: [tgbot-health, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 进程问询必实查 tgbot/bus/VPN/打卡/away-health，并区分产线数据告警与本机 daemon 状态

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

进程问询必实查 tgbot/bus/VPN/打卡/away-health，并区分产线数据告警与本机 daemon 状态

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
