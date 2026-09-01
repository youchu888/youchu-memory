---
date: 2026-09-01
tags: [workbook, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 读到群簿或有大活交付后，当天同步 task 板 + supplemental + work-log，大活后再补发进展，禁止只依赖 09:01 一次

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

读到群簿或有大活交付后，当天同步 task 板 + supplemental + work-log，大活后再补发进展，禁止只依赖 09:01 一次

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
