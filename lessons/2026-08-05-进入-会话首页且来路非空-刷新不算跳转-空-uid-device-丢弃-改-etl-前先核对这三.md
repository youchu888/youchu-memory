---
date: 2026-08-05
tags: [page-visit-caliber, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 进入=会话首页且来路非空；刷新不算跳转；空 uid/device 丢弃——改 ETL 前先核对这三条

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

进入=会话首页且来路非空；刷新不算跳转；空 uid/device 丢弃——改 ETL 前先核对这三条

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
