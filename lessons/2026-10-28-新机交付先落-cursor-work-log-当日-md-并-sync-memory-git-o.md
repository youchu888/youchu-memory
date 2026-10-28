---
date: 2026-10-28
tags: [dual-machine-sync,memory-git, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 新机交付先落 `.cursor/work-log/当日.md` 并 `sync-memory-git`，old-mac 汇总前必跑 `prepare_daily

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

新机交付先落 `.cursor/work-log/当日.md` 并 `sync-memory-git`，old-mac 汇总前必跑 `prepare_daily_report_sync.sh`，缺 hosts 文件要明示缺哪台

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
