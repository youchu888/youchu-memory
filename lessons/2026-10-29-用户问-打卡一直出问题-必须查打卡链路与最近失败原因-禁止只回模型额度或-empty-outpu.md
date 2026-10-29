---
date: 2026-10-29
tags: [punch-attendance, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户问「打卡一直出问题」必须查打卡链路与最近失败原因，禁止只回模型额度或 empty output 模板

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户问「打卡一直出问题」必须查打卡链路与最近失败原因，禁止只回模型额度或 empty output 模板

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
