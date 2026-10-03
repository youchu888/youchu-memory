---
date: 2026-10-03
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# upload|上传云端以 reports/日报-YYYY-MM-DD.md 定稿为准、指定日期原封不动提交，禁止边传边改正文

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

upload|上传云端以 reports/日报-YYYY-MM-DD.md 定稿为准、指定日期原封不动提交，禁止边传边改正文

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
