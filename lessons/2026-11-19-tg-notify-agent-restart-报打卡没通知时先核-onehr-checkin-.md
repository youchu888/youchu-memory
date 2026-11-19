---
date: 2026-11-19
tags: [onehr-checkin, session-rotate, self-evolve]
severity: medium
domain: ops
---

# tg-notify|agent-restart|报打卡没通知时先核 onehr-checkin + 当日打卡成功 + 日志 TG 失败；进程正常仍要区分推送断点

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

tg-notify|agent-restart|报打卡没通知时先核 onehr-checkin + 当日打卡成功 + 日志 TG 失败；进程正常仍要区分推送断点，并向用户要断档起始日再细查

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
