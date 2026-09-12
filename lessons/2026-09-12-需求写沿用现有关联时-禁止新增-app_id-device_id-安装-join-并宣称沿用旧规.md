---
date: 2026-09-12
tags: [归因入围, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 需求写沿用现有关联时，禁止新增 app_id+device_id 安装 JOIN 并宣称沿用旧规则

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

需求写沿用现有关联时，禁止新增 app_id+device_id 安装 JOIN 并宣称沿用旧规则

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
