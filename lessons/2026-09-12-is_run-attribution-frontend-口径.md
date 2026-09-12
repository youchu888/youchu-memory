---
date: 2026-09-12
tags: [dim_app_attribution_config, session-rotate, self-evolve]
severity: medium
domain: ops
---

# is_run|attribution|frontend|口径

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

is_run|attribution|frontend|口径

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
