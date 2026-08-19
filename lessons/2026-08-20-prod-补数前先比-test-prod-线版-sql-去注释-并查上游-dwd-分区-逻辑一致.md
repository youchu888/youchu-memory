---
date: 2026-08-20
tags: [complement,comic-analysis, session-rotate, self-evolve]
severity: medium
domain: ops
---

# prod 补数前先比 test/prod 线版 SQL（去注释）并查上游 DWD 分区，逻辑一致且上游有数再用 TASK_ONLY 串行补缺口分区

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

prod 补数前先比 test/prod 线版 SQL（去注释）并查上游 DWD 分区，逻辑一致且上游有数再用 TASK_ONLY 串行补缺口分区

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
