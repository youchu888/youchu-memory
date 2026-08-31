---
date: 2026-09-01
tags: [spark-scheduler,pipeline-runner, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 加 Spark 任务只改 SQL + steps.json 挂槽位，tagTargets 必填，先 explain 试跑，禁止动生产 full_chain.js

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

加 Spark 任务只改 SQL + steps.json 挂槽位，tagTargets 必填，先 explain 试跑，禁止动生产 full_chain.json

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
