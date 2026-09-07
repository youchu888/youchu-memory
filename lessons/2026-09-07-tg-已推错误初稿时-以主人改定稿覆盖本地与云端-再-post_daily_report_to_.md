---
date: 2026-09-07
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# TG 已推错误初稿时，以主人改定稿覆盖本地与云端，再 `post_daily_report_to_dm.py --force` 重推，勿在 upload 前改定

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

TG 已推错误初稿时，以主人改定稿覆盖本地与云端，再 `post_daily_report_to_dm.py --force` 重推，勿在 upload 前改定稿正文

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
