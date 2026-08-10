---
date: 2026-08-11
tags: [daily-report,cloud-upload, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 用户说「推送云端」时只传已定稿 reports 文件，禁止改写；成功回执须含云端 record id 与 inserted/updated 状态

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

用户说「推送云端」时只传已定稿 reports 文件，禁止改写；成功回执须含云端 record id 与 inserted/updated 状态

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
