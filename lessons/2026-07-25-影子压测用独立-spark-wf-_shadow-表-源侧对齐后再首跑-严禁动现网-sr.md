---
date: 2026-07-25
tags: [paimon-shadow, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 影子压测用独立 Spark wf + `_shadow` 表，源侧对齐后再首跑，严禁动现网 SR

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

影子压测用独立 Spark wf + `_shadow` 表，源侧对齐后再首跑，严禁动现网 SR

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
