---
date: 2026-08-14
tags: [task-priority, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 派活默认闭环：一次性独立任务（如 _probe 上集群）不因盯盘/回执让路 indefinitely；回了「今天给」须立刻提交或查现场

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

派活默认闭环：一次性独立任务（如 _probe 上集群）不因盯盘/回执让路 indefinitely；回了「今天给」须立刻提交或查现场

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
