---
date: 2026-11-23
tags: [agent-bus,tgbot, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 主人说 bus/机器人没收到时，先查 inbox+TG 镜像时间线；自动执行快速结案优先解释「看不见」，再改推送文案

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

主人说 bus/机器人没收到时，先查 inbox+TG 镜像时间线；自动执行快速结案优先解释「看不见」，再改推送文案

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
