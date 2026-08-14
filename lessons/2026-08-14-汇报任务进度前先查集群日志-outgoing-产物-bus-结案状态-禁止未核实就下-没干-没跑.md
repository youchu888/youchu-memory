---
date: 2026-08-14
tags: [agent-execution, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 汇报任务进度前先查集群日志、outgoing 产物、bus 结案状态，禁止未核实就下「没干/没跑」结论

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

汇报任务进度前先查集群日志、outgoing 产物、bus 结案状态，禁止未核实就下「没干/没跑」结论

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
