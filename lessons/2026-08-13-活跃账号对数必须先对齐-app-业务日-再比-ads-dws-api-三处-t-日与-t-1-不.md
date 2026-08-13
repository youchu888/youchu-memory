---
date: 2026-08-13
tags: [datacheck, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 活跃账号对数必须先对齐 app+业务日，再比 ads/dws/API 三处；T 日与 T-1 不可混比

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

活跃账号对数必须先对齐 app+业务日，再比 ads/dws/API 三处；T 日与 T-1 不可混比

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
