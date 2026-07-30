---
date: 2026-07-31
tags: [attribution, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 答疑「没匹配为何有分」先看 `attribution_status`/`unattributed_reason`，有分只说明命中候选；成功需 `score >=

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

答疑「没匹配为何有分」先看 `attribution_status`/`unattributed_reason`，有分只说明命中候选；成功需 `score >= score_threshold`

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
