---
date: 2026-09-01
tags: [workbook, session-rotate, self-evolve]
severity: medium
domain: ops
---

# task 板与 work-log 超过 1 天未对齐即执行缺口，先刷新 task 板再答进展问

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

task 板与 work-log 超过 1 天未对齐即执行缺口，先刷新 task 板再答进展问

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
