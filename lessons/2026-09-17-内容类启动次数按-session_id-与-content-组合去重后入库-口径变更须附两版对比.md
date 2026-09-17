---
date: 2026-09-17
tags: [大漏斗, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 内容类启动次数按 session_id 与 content 组合去重后入库，口径变更须附两版对比供产品确认

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

内容类启动次数按 session_id 与 content 组合去重后入库，口径变更须附两版对比供产品确认

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
