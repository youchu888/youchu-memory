---
date: 2026-09-08
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户贴定稿说「上传云端」时正文零改写，先落 `.cursor/work-log/reports/日报-日期.md` 再调脚本，回执带 record ID 与状态

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户贴定稿说「上传云端」时正文零改写，先落 `.cursor/work-log/reports/日报-日期.md` 再调脚本，回执带 record ID 与状态

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
