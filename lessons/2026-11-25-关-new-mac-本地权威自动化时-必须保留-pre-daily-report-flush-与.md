---
date: 2026-11-25
tags: [daily-report,new-mac,automation, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 关 new-mac 本地权威自动化时，必须保留 pre-daily-report-flush 与 memory-git-sync，否则双机 work-log 断

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

关 new-mac 本地权威自动化时，必须保留 pre-daily-report-flush 与 memory-git-sync，否则双机 work-log 断流。

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
