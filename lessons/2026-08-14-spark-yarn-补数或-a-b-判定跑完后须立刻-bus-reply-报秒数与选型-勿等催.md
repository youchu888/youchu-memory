---
date: 2026-08-14
tags: [agent-bus, session-rotate, self-evolve]
severity: medium
domain: ops
---

# Spark/YARN 补数或 A/B 判定跑完后须立刻 bus reply 报秒数与选型，勿等催办才回执

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

Spark/YARN 补数或 A/B 判定跑完后须立刻 bus reply 报秒数与选型，勿等催办才回执

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
