---
date: 2026-08-13
tags: [keyword-analysis, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 关键词页空白先查 ops-api 路由是否 404，prod 活表仅 d_h/search_hour_d，勿猜不存在的 d_d 表

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

关键词页空白先查 ops-api 路由是否 404，prod 活表仅 d_h/search_hour_d，勿猜不存在的 d_d 表

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
