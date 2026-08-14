---
date: 2026-08-15
tags: [daily-report,upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户贴定稿并说「按这个上传云端」时，先写 reports/日报-日期.md 再 upload，API 正文与用户所给完全一致，成功后回执日期/记录 ID/状态即

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户贴定稿并说「按这个上传云端」时，先写 reports/日报-日期.md 再 upload，API 正文与用户所给完全一致，成功后回执日期/记录 ID/状态即可

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
