---
date: 2026-08-18
tags: [dbprogramming, session-rotate, self-evolve]
severity: medium
domain: ops
---

# test SR 建表走 dev session + MCP DDL；Paimon/staging 另跑 Hadoop `run_paimon_ddl.sh`，交

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

test SR 建表走 dev session + MCP DDL；Paimon/staging 另跑 Hadoop `run_paimon_ddl.sh`，交付时分环境说明

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
