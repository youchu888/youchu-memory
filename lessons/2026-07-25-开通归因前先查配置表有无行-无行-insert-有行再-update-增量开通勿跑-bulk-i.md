---
date: 2026-07-25
tags: [attribution,prod-config, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 开通归因前先查配置表有无行；无行 INSERT、有行再 UPDATE；增量开通勿跑 bulk is_run=0

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

开通归因前先查配置表有无行；无行 INSERT、有行再 UPDATE；增量开通勿跑 bulk is_run=0

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
