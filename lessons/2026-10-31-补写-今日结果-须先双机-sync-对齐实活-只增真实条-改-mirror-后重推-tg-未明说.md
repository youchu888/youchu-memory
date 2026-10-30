---
date: 2026-10-31
tags: [daily-report,supplement,tg, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 补写【今日结果】须先双机 sync 对齐实活，只增真实条、改 mirror 后重推 TG；未明说「上传云端」则不上传

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

补写【今日结果】须先双机 sync 对齐实活，只增真实条、改 mirror 后重推 TG；未明说「上传云端」则不上传

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
