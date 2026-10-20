---
date: 2026-10-20
tags: [dev-session,dolphin-withdraw,spark, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 海豚待发布撤回后统一 Spark 化重走七步；被新版本覆盖或已有 Spark 续作的 session 标记过时，避免重复发海豚或重复立项。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

海豚待发布撤回后统一 Spark 化重走七步；被新版本覆盖或已有 Spark 续作的 session 标记过时，避免重复发海豚或重复立项。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
