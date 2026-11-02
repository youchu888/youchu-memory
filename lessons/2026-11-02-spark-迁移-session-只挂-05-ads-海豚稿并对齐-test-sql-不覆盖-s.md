---
date: 2026-11-02
tags: [dev-session,spark_migrate,dolphin, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Spark 迁移 session 只挂 05.ads 海豚稿并对齐 test SQL；不覆盖 spark_migrate 周表稿，并清理月表目录 spark 残

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Spark 迁移 session 只挂 05.ads 海豚稿并对齐 test SQL；不覆盖 spark_migrate 周表稿，并清理月表目录 spark 残留后再提审。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
