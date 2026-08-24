---
date: 2026-08-24
tags: [tgbot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 绿点|打卡|问机制先读 `should_appear_online()` 与计划时间生成，勿把 `JIKE_CHECKIN_ENABLED` 当成绿点开关

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

绿点|打卡|问机制先读 `should_appear_online()` 与计划时间生成，勿把 `JIKE_CHECKIN_ENABLED` 当成绿点开关

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
