---
date: 2026-10-12
tags: [渠道周月表,ads_channel_promotion, session-rotate, self-evolve]
severity: medium
domain: ops
---

# 周月充值三列对 ads.ads_channel_promotion_summary_d 同期 SUM（VIP / 扣量 VIP / 金币）；新增与次留禁止按日相

## 背景

TG Cursor 共用会话轮换前自动蒸馏（session-rotate）。

## 正确做法

周月充值三列对 ads.ads_channel_promotion_summary_d 同期 SUM（VIP / 扣量 VIP / 金币）；新增与次留禁止按日相加

## 验证

下一会话 prompt 携带 `tgbot_session_carry.md` 能看到同类要点。

## 关联

- 来源：agent_session_rotate / session_memory_distill
