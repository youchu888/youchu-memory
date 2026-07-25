---
date: 2026-07-25
tags: [attribution, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 开通归因=配置表 is_run=1 + 客户端 attribution_flag:1 双开，诊断报告后须确认是否已执行

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

开通归因=配置表 is_run=1 + 客户端 attribution_flag:1 双开，诊断报告后须确认是否已执行

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
