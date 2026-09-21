---
date: 2026-09-20
tags: [daily-report,upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 主人贴定稿要求上传云端时，先原样落盘 reports/ 再跑 upload_work_report.py，禁止改写正文后再传

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

主人贴定稿要求上传云端时，先原样落盘 reports/ 再跑 upload_work_report.py，禁止改写正文后再传

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
