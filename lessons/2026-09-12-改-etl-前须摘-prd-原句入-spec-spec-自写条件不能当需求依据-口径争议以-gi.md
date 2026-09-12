---
date: 2026-09-12
tags: [需求对齐, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 改 ETL 前须摘 PRD 原句入 spec；spec 自写条件不能当需求依据，口径争议以 git diff 为准

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

改 ETL 前须摘 PRD 原句入 spec；spec 自写条件不能当需求依据，口径争议以 git diff 为准

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
