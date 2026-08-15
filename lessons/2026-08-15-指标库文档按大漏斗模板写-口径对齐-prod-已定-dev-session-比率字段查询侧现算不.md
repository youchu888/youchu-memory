---
date: 2026-08-15
tags: [metric-library,page-visit, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 指标库文档按大漏斗模板写，口径对齐 prod/已定 dev session，比率字段查询侧现算不落库，定稿上传平台后以库页为唯一权威源

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

指标库文档按大漏斗模板写，口径对齐 prod/已定 dev session，比率字段查询侧现算不落库，定稿上传平台后以库页为唯一权威源

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
