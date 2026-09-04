---
date: 2026-09-04
tags: [funnel, session-rotate, self-evolve]
severity: medium
domain: ops
---

# test 验收须全 app 空 filter 跑完 stage_metrics→stage_wide（`sandbox_steps_full.json` 槽 0

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

test 验收须全 app 空 filter 跑完 stage_metrics→stage_wide（`sandbox_steps_full.json` 槽 00），单 SF-81 冒烟不能当交付

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
