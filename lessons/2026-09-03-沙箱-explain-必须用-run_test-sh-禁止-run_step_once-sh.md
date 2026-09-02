---
date: 2026-09-03
tags: [sandbox-explain, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 沙箱 explain 必须用 run_test.sh，禁止 run_step_once.sh

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

沙箱 explain 必须用 run_test.sh，禁止 run_step_once.sh

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
