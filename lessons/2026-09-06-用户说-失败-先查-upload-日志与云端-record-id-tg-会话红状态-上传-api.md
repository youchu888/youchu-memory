---
date: 2026-09-06
tags: [daily-report,upload,tg, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户说「失败」先查 upload 日志与云端 record ID；TG 会话红状态≠上传 API 失败，须分开核对

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户说「失败」先查 upload 日志与云端 record ID；TG 会话红状态≠上传 API 失败，须分开核对

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
