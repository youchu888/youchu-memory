---
date: 2026-11-04
tags: [口径, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 问「渠道从哪来」先分清：归因前→DWD.channel；产品周/月→渠道日指标→dim_channel 归部门，日表 channel 多数来自 dim_user

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

问「渠道从哪来」先分清：归因前→DWD.channel；产品周/月→渠道日指标→dim_channel 归部门，日表 channel 多数来自 dim_user_all

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
