---
date: 2026-09-06
tags: [daily-report,upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 同日重复上传云端是 updated 覆盖同一条记录，inserted→updated 属正常，勿误判为异常

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

同日重复上传云端是 updated 覆盖同一条记录，inserted→updated 属正常，勿误判为异常

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
