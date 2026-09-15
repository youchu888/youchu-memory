---
date: 2026-09-15
tags: [daily-report,flush, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 新机实活交付后须写入该机 `.cursor/work-log/当日.md` 并 sync-memory-git，否则旧机 21:30 写稿必漏

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

新机实活交付后须写入该机 `.cursor/work-log/当日.md` 并 sync-memory-git，否则旧机 21:30 写稿必漏

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
