---
date: 2026-10-28
tags: [model-quota-vs-task, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 遇全链 fallback 额度提示时，简短说明对话模型受限，同步/查数类问题仍按 runbook 逐步答，勿重复空模板忽略主人原问

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

遇全链 fallback 额度提示时，简短说明对话模型受限，同步/查数类问题仍按 runbook 逐步答，勿重复空模板忽略主人原问

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
