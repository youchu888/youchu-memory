---
date: 2026-09-01
tags: [progress-report,agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 主人要任务进度时用人话逐项写节点/卡点/需确认项，并实查 task 板+work-log+git，禁止流水账或凭会话记忆

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

主人要任务进度时用人话逐项写节点/卡点/需确认项，并实查 task 板+work-log+git，禁止流水账或凭会话记忆

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
