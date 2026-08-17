---
date: 2026-08-17
tags: [agent-bus,补发, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 原 bus 被误结案后补正式回执须 `--no-dedup` 新发 reply，并检查 dedup 是否再次拦截

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

原 bus 被误结案后补正式回执须 `--no-dedup` 新发 reply，并检查 dedup 是否再次拦截

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
