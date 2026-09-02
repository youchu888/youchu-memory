---
date: 2026-09-02
tags: [daily-report,cloud-upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 定稿推 TG ≠ 已上传云端；核对须分开查 dm_posted 与 upload 脚本执行记录

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

定稿推 TG ≠ 已上传云端；核对须分开查 dm_posted 与 upload 脚本执行记录

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
