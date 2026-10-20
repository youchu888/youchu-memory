---
date: 2026-10-20
tags: [datacheck,dolphin,ddl-etl-gap, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 表上新列但任务不写时，以海豚 live INSERT 列清单为准判是否发版，并对照同批 task 排查漏发/半截版。

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

表上新列但任务不写时，以海豚 live INSERT 列清单为准判是否发版，并对照同批 task 排查漏发/半截版。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
