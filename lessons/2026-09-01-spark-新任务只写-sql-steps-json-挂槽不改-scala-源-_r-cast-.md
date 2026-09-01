---
date: 2026-09-01
tags: [spark-steps, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Spark 新任务只写 SQL+steps.json 挂槽不改 Scala；源 `_r`、CAST、`tagTargets` 必填；先沙箱 fragment，别

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Spark 新任务只写 SQL+steps.json 挂槽不改 Scala；源 `_r`、CAST、`tagTargets` 必填；先沙箱 fragment，别直接改 prod full_chain

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
