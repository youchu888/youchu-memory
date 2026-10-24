---
date: 2026-10-24
tags: [dev-session,dolphin_prod, session-rotate, self-evolve]
severity: medium
domain: ops
---

# stage7 且 publish_runs_count=0 即未产发，产表 0 行属正常，需先审过挂编排再验数

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

stage7 且 publish_runs_count=0 即未产发，产表 0 行属正常，需先审过挂编排再验数

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
