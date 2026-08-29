---
date: 2026-08-29
tags: [metric-library,G5,application-layer, session-rotate, self-evolve]
severity: medium
domain: ops
---

# G5「库内违规=0」≠ 应用层已落地；复验须分开报库内数据与 service/router 是否做 G4/G5 validate

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

G5「库内违规=0」≠ 应用层已落地；复验须分开报库内数据与 service/router 是否做 G4/G5 validate

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
