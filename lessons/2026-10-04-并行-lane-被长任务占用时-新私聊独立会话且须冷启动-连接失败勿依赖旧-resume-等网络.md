---
date: 2026-10-04
tags: [tg-parallel-agent, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 并行 lane 被长任务占用时，新私聊独立会话且须冷启动；连接失败勿依赖旧 resume，等网络恢复后让用户重发原句

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

并行 lane 被长任务占用时，新私聊独立会话且须冷启动；连接失败勿依赖旧 resume，等网络恢复后让用户重发原句

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
