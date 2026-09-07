---
date: 2026-09-07
tags: [daily-report, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 写日报前须双机 sync 后合并 work-log + 全量 transcript + 派单来源；work-log 噪音大时不能单靠流水，否则易漏跨主题实活

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

写日报前须双机 sync 后合并 work-log + 全量 transcript + 派单来源；work-log 噪音大时不能单靠流水，否则易漏跨主题实活

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
