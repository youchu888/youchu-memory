---
date: 2026-08-13
tags: [datacheck,API, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 活跃数核查统一走用户活跃 V2 与 `dau_count`，V1 仅 PV 会系统性偏低

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

活跃数核查统一走用户活跃 V2 与 `dau_count`，V1 仅 PV 会系统性偏低

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
