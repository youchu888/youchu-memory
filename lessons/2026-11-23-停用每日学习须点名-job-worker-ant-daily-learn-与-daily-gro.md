---
date: 2026-11-23
tags: [launchd,每日学习, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 停用每日学习须点名 job：`worker-ant-daily-learn` 与 `daily-group-learn` 分开确认，未卸后者则 02:00 群聊

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

停用每日学习须点名 job：`worker-ant-daily-learn` 与 `daily-group-learn` 分开确认，未卸后者则 02:00 群聊汇总仍会推私聊

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
