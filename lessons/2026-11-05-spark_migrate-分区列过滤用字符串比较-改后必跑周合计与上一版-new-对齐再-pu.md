---
date: 2026-11-05
tags: [spark-partition-where, session-rotate, self-evolve]
severity: medium
domain: ops
---

# spark_migrate 分区列过滤用字符串比较，改后必跑周合计与上一版 new 对齐再 push

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

spark_migrate 分区列过滤用字符串比较，改后必跑周合计与上一版 new 对齐再 push

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
