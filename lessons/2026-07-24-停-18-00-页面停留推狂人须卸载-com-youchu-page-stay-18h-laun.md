---
date: 2026-07-24
tags: [page-stay,launchd,agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 停 18:00 页面停留推狂人须卸载 `com.youchu.page-stay-18h` launchd，勿只改脚本不卸定时

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

停 18:00 页面停留推狂人须卸载 `com.youchu.page-stay-18h` launchd，勿只改脚本不卸定时

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
