---
date: 2026-10-25
tags: [pipeline-runner, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 值班查异常先 heartbeat + 筛真实 `runner_` 告警；`wait_probe`/探针 block 且主链 slot_done 只观察，长期不动

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

值班查异常先 heartbeat + 筛真实 `runner_` 告警；`wait_probe`/探针 block 且主链 slot_done 只观察，长期不动或反复失败再 runbook/补数

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
