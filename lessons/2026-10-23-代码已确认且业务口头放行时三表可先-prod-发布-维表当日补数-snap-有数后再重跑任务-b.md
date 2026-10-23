---
date: 2026-10-23
tags: [dolphin_prod,agent-bus,维表补数, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 代码已确认且业务口头放行时三表可先 prod 发布；维表当日补数、snap 有数后再重跑任务；bus 去重误拦时用 `--no-dedup` 重发

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

代码已确认且业务口头放行时三表可先 prod 发布；维表当日补数、snap 有数后再重跑任务；bus 去重误拦时用 `--no-dedup` 重发

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
