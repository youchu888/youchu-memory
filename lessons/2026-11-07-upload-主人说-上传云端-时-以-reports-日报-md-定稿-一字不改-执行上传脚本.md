---
date: 2026-11-07
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# upload|主人说「上传云端」时，以 `reports/日报-*.md` 定稿**一字不改**执行上传脚本

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

upload|主人说「上传云端」时，以 `reports/日报-*.md` 定稿**一字不改**执行上传脚本

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
