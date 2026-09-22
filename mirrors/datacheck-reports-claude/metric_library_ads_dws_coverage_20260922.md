# 指标库 · ads+dws online 覆盖对照表

> 生成：2026-09-22 · test metadata · **只读盘点，未改库**
> 范围：`tabledefinition.release_status=online` 且 database∈{ads,dws}
> 规则：B 路线（分批定稿）；本表过目后再动手

## 总览

| 项 | 数 |
|----|----|
| online 表（ads+dws） | 0 |
| 已挂（有 active implementation） | 0 |
| 部分挂（有实现但仍有疑似指标列未挂） | 0 |
| 未挂 | 0 |
| 疑似指标列合计（启发式） | 0 |
| 其中尚未挂到 implementation 的列 | 0 |
| 库内 metric_concept published/orphaned | 301 / 11 |
| 库内 active implementation | 419 |

说明：「疑似指标列」= 列名含 cnt/uv/pv/amount/revenue… 等，或 BIGINT/DOUBLE/BITMAP 等度量型，并去掉 dt/app_id/channel 等常见维度。**启发式，不是最终清单**；正式扫表进 candidate 时还会再挡一刀。

## 建议第一批（活跃域）候选表

| 表 | 状态 | 疑似列 | 已挂实现 | 未挂列数 |
|----|------|--------|----------|----------|

## 全表明细

| 库 | 表 | 状态 | 总列 | 疑似指标列 | 已挂实现数 | 涉及concept | 旧binding | 未挂列数 | 未挂列样例 |
|----|----|------|------|------------|------------|-------------|-----------|----------|------------|

## 附：有实现但不在 online 清单的 ads/dws 表

这些实现挂在非 online（或元数据未登记）表上，填数时默认不扩范围；需要时另议。

| 表 | active实现 | concept数 |
|----|------------|-----------|
| `ads.ads_action_page_funnel_d` | 7 | 7 |
| `ads.ads_ad_space_summary_d` | 7 | 7 |
| `ads.ads_app_active_summary` | 2 | 2 |
| `ads.ads_app_metrics_daily_d` | 31 | 31 |
| `ads.ads_app_metrics_hourly_d` | 12 | 12 |
| `ads.ads_app_summary_d` | 10 | 10 |
| `ads.ads_channel_daily_funnel_report_d` | 21 | 21 |
| `ads.ads_channel_metrics_daily_d` | 18 | 18 |
| `ads.ads_channel_promotion_summary_d` | 17 | 17 |
| `ads.ads_channel_promotion_summary_h` | 15 | 15 |
| `ads.ads_channel_summary_d` | 10 | 10 |
| `ads.ads_page_heatmap_d` | 4 | 4 |
| `ads.ads_product_day_stat_d` | 41 | 41 |
| `ads.ads_user_dormancy_d` | 10 | 10 |
| `ads.ads_user_page_path_d` | 2 | 2 |
| `ads.ads_user_retention_d` | 18 | 18 |
| `dws.dws_app_channel_dau_d` | 3 | 3 |
| `dws.dws_app_channel_deduction_d` | 9 | 9 |
| `dws.dws_app_channel_deduction_h` | 9 | 9 |
| `dws.dws_app_channel_retention_d` | 4 | 4 |
| `dws.dws_app_channel_summary_d` | 13 | 13 |
| `dws.dws_app_channel_summary_h` | 11 | 11 |
| `dws.dws_app_order_d` | 6 | 6 |
| `dws.dws_app_retention_d` | 31 | 31 |
| `dws.dws_app_user_d` | 5 | 5 |
| `dws.dws_app_user_m` | 5 | 5 |
| `dws.dws_app_user_w` | 5 | 5 |
| `dws.dws_channel_daily_funnel_d` | 9 | 9 |
| `dws.dws_recharge_composition_user_h` | 4 | 4 |
| `dws.dws_register_by_landing_page_d` | 1 | 1 |
| `dws.dws_user_first_recharge_retention_d` | 31 | 31 |
| `dws.dws_user_promotion_behavior_charge_d` | 4 | 4 |
| `dws.dws_user_promotion_behavior_charge_h` | 1 | 1 |
| `dws.dws_user_promotion_behavior_d` | 5 | 5 |
| `dws.dws_user_promotion_behavior_h` | 2 | 2 |
| `dws.dws_user_reg_ltv_daily_d` | 32 | 32 |
| `dws.dws_user_reg_video_funnel_daily_d` | 4 | 4 |

## 下一步（等你点头）

1. 你过目本表，标「先做 / 后做 / 不做」
2. 又初开第一批：**活跃域**（上表建议第一批）→ 扫入 candidate → 按 D1 规则定稿升 published
3. 一批一结，再开注册/留存、充值…
