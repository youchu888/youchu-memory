---
date: 2026-08-07
tags: [workbook-progress,prod-check, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 群工作簿进度发群前必须 prod 实查分区/验数，禁止只看 test 或 dev session pending 状态

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

群工作簿进度发群前必须 prod 实查分区/验数，禁止只看 test 或 dev session pending 状态

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
