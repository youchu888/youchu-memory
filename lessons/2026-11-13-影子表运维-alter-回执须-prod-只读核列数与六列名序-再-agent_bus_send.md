---
date: 2026-11-13
tags: [agent-bus,sr-shadow,ddl-receipt, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 影子表运维 ALTER 回执须 prod 只读核列数与六列名序，再 `agent_bus_send --reply-to-bus-id`；去重拦实质内容时用 `

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

影子表运维 ALTER 回执须 prod 只读核列数与六列名序，再 `agent_bus_send --reply-to-bus-id`；去重拦实质内容时用 `--no-dedup` 重发。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
