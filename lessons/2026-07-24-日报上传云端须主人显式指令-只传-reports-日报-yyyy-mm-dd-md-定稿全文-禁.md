---
date: 2026-07-24
tags: [daily-report,upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 日报上传云端须主人显式指令；只传 `reports/日报-YYYY-MM-DD.md` 定稿全文，禁止改字或夹带其它文件

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

日报上传云端须主人显式指令；只传 `reports/日报-YYYY-MM-DD.md` 定稿全文，禁止改字或夹带其它文件

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
