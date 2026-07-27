---
date: 2026-07-28
tags: [device_tag,dim, session-rotate, self-evolve]
severity: medium
domain: ops
---

# device_id 空率≥90%（本需求 100%）则直建 dim_device_all，勿再设计 uid 反查兜底

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

device_id 空率≥90%（本需求 100%）则直建 dim_device_all，勿再设计 uid 反查兜底

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
