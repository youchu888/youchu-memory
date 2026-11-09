---
date: 2026-11-10
tags: [agent-bus,tg, session-rotate, self-evolve]
severity: medium
domain: ops
---

# ack 若 `dropped=silent`，用 `--no-dedup` 或 progress 顶替，勿把未收到 ack 当已 ack。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

ack 若 `dropped=silent`，用 `--no-dedup` 或 progress 顶替，勿把未收到 ack 当已 ack。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
