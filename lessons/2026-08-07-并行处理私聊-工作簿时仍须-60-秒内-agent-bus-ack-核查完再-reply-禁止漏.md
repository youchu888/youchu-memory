---
date: 2026-08-07
tags: [agent-bus,ack, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 并行处理私聊/工作簿时仍须 60 秒内 agent-bus ACK，核查完再 reply，禁止漏单

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

并行处理私聊/工作簿时仍须 60 秒内 agent-bus ACK，核查完再 reply，禁止漏单

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
