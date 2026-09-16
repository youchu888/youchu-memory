---
date: 2026-09-16
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户私聊贴完整定稿并说「按这个上传云端」时，以粘贴正文落盘再调 upload_work_report，禁止按 work-log 或会话重生成正文

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户私聊贴完整定稿并说「按这个上传云端」时，以粘贴正文落盘再调 upload_work_report，禁止按 work-log 或会话重生成正文

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
