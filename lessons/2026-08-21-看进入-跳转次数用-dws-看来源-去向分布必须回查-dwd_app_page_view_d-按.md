---
date: 2026-08-21
tags: [dws-app-page-visit, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 看进入/跳转次数用 DWS；看来源→去向分布必须回查 dwd_app_page_view_d 按 referrer_page_key+page_key 聚合

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

看进入/跳转次数用 DWS；看来源→去向分布必须回查 dwd_app_page_view_d 按 referrer_page_key+page_key 聚合

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
