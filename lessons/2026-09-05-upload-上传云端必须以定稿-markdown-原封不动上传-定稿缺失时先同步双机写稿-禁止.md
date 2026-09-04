---
date: 2026-09-05
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# upload|上传云端必须以定稿 Markdown 原封不动上传；定稿缺失时先同步双机写稿，禁止边传边改

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

upload|上传云端必须以定稿 Markdown 原封不动上传；定稿缺失时先同步双机写稿，禁止边传边改

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
