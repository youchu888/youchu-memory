---
date: 2026-11-19
source: worker_ant_group @anna_cute9
tags: charge_d, ads_channel_promotion_summary_d, paimon_shadow, dolphin, caliber, parallel
---

# charge_d / summary_d 正式表与 Paimon 影子双链路并行（群 2026-11-19）

（正文与项目 `.claude/memory/lessons/2026-11-19-charge-summary-正式表与paimon影子双链路并行.md` 同步）

## 正式表

- `dws_user_promotion_behavior_charge_d`：海豚 SR SQL；event_time 切天；结算明细 order_paid + 当日注册用户。
- `ads_channel_promotion_summary_d`：三张渠道日表 SR 关联；`wf_渠道分析_日`；summary 无仓内独立 SQL，现网以海豚为准。

## 影子表

- Spark 小时→日；request_time 切、不回看；与正式 event_time 差异为预期。
- SQL：`b3_charge_*`、`b4_ads_summary_*` 路径见项目 lesson 全文。