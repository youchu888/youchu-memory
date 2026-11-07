---
date: 2026-11-08
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# upload|上传前锁定定稿文件，禁止改字；仅主人要求「上传云端」时跑脚本，成功回 code 与稿路径

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

upload|上传前锁定定稿文件，禁止改字；仅主人要求「上传云端」时跑脚本，成功回 code 与稿路径

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
