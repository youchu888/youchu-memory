---
date: 2026-10-23
tags: [mgmt-report,prod-gate, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 三表挂 prod 前先查 prod Paimon 是否存在 `ads_channel_metrics_daily_d` 及编排步，缺则先走完并审发 013，勿只

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

三表挂 prod 前先查 prod Paimon 是否存在 `ads_channel_metrics_daily_d` 及编排步，缺则先走完并审发 013，勿只修 snap/SR

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
