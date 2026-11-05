---
date: 2026-11-06
tags: [tg-green-dot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 现网绿点只看 tgbot dispatch 的 visible-online 日志；Telethon watcher 异常退出则重启 tgbot，勿误判 tg-

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

现网绿点只看 tgbot dispatch 的 visible-online 日志；Telethon watcher 异常退出则重启 tgbot，勿误判 tg-work-online launchd 为保活主路径

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
