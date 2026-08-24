---
date: 2026-08-25
tags: [doc-library,delivery, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 指标库 ER 推文档库后须同步落仓 `docs/metric_library_er_diagram_*.{html,md}` 并在回执里给 slug、打开链接与

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

指标库 ER 推文档库后须同步落仓 `docs/metric_library_er_diagram_*.{html,md}` 并在回执里给 slug、打开链接与图层配色说明

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
