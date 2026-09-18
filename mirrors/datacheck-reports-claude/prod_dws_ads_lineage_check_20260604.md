# 生产 DWS / ADS 血缘核对报告

| 项 | 内容 |
|----|------|
| 检查时间 | 2026-06-04 |
| 方法 | 各表 `MAX(dt)` + 近 7 日行数；对照仓库 ETL 物理 `FROM` 与 lineage_playbook / lesson |
| 上游抽样 | `dwd_user_register_d_v2`、`dwd_order_*`、`dwd_app_page_view_d`、`dwd_landing_page_*` |

## 上游基线（DWD）

| 上游 | MAX(dt) | 说明 |
|------|---------|------|
| dwd_user_register_d_v2 | 2026-06-04 | 与小时 DWS 同步 |
| dwd_order_paid_d / dwd_order_created_h | 2026-06-04 | |
| dwd_app_page_view_d | 2026-06-04 | 留存/漏斗 |
| dwd_landing_page_view_d / click_d | **2026-06-03** | 比注册晚 1 天，归因 T+1 正常 |

## 汇总

| 库 | 物理表 | lag=0 当日 | lag=1 T+1 | 空表/停更 | 无 dt |
|----|--------|:----------:|:---------:|:---------:|:-----:|
| dws | 37 | 8 | 9 | 4 | 16 |
| ads | 29 | 7 | 3 | 7 | 12 |

**说明**：小时表 `_h`、Flink 日表多为 **lag=0**；日批 `*_d`、归因、渠道漏斗多为 **lag=1**。无 `dt` 多为汇总宽表或 `date_key` 口径。

---

## 一、核心链路（血缘 + 核对结果）

### 1. 活跃 → 指标 → 项目日报

```
dwd_app_page_view_d ─┐
dwd_user_register ───┼→ dws_app_user_d_h (lag=0) ─→ ads_app_metrics_daily/hourly (lag=0)
                     └→ dws_app_retention_d_h (lag=0) ─→ MV ads_user_retention_d (18:05 SUCCESS)
                                                              └→ ads_product_day_stat_d (lag=0)
```

| 节点 | MAX(dt) | 与上游 | 结论 |
|------|---------|--------|------|
| dws_app_user_d_h | 06-04 | DWD 06-04 | ✅ |
| dws_app_retention_d_h | 06-04 | DWD 06-04 | ✅ |
| ads_app_metrics_daily_d | 06-04 | 依赖 user_h | ✅ |
| ads_app_metrics_hourly_d | 06-04 | | ✅ |
| ads_user_retention_d (MV) | 刷新 06-04 18:05 | 来自 retention_h | ✅ |
| ads_product_day_stat_d | 06-04 | 依赖 metrics+retention+channel_promo+订单 | ✅ 已追上当日 |

### 2. 订单 → 订单小时 → 日报

```
dwd_order_created_h / dwd_order_paid_d ─→ dws_app_order_d_h (lag=0)
                                        └→ ads_product_day_stat_d（订单段）
```

| 节点 | MAX(dt) | 结论 |
|------|---------|------|
| dws_app_order_d_h | 06-04 | ✅ 有数（02:12 曾 BE rpc 失败，需关注 slot 完整性） |
| 上游 DWD 订单 | 06-04 | ✅ |

### 3. LTV（reg cohort）

```
dim_user_all + dwd_order_paid_d ─→ dws_user_reg_ltv_d_h (lag=0)
                                 └→ dws_user_reg_ltv_daily_d（VIEW，旧物理 dws_user_reg_ltv_daily_d_old lag=7）
```

| 节点 | MAX(dt) | 结论 |
|------|---------|------|
| dws_user_reg_ltv_d_h | 06-04 | ✅ |
| dws_user_reg_ltv_daily_d_old | 05-28 | ⚠️ 弃用物理表，应用 VIEW + 日批 |

### 4. 注册归因

```
dwd_user_register + dwd_landing_page_* + dim_app_attribution_config
  ─→ dws_register_attribution_result_d (lag=1, MAX=06-03)
```

| 节点 | MAX(dt) | 结论 |
|------|---------|------|
| 上游落地页 | 06-03 | ✅ 与归因一致 |
| dws_register_attribution_result_d | 06-03 | ✅ T+1；06-04 注册待明日批 |

### 5. 首充留存 / 推广行为

```
dwd_order_paid + dim ─→ dws_user_first_recharge_retention_d_h (lag=1)
                     └→ dws_user_promotion_behavior_{d,h} (日 lag=1 / 时 lag=0)
```

| 节点 | 结论 |
|------|------|
| first_recharge_retention_d_h | ✅ T+1 |
| promotion_behavior_h / charge_h | ✅ 小时当日 |

### 6. 渠道 / 结算（无 dt 或特殊分区）

| 表 | 状态 |
|----|------|
| dws_app_channel_summary_h/d、ads_channel_promotion_summary_h/d | 有数据，无 `dt` 字段（用 date_key 等） |
| dws_settlement_detail | 大行数，结算宽表 |
| dws_channel_daily_funnel_d | lag=1 ✅ |

---

## 二、DWS 全表清单

| 表 | MAX(dt) | 落后 | 近7d行数 | 血缘角色 / 备注 |
|----|---------|:----:|---------:|-----------------|
| dws_app_user_d_h | 06-04 | 0 | 22M | 活跃小时，ADS 指标上游 |
| dws_app_retention_d_h | 06-04 | 0 | 10M | 留存小时 → MV retention |
| dws_app_order_d_h | 06-04 | 0 | 308K | 订单小时 |
| dws_user_reg_ltv_d_h | 06-04 | 0 | 10M | LTV 主表 |
| dws_user_finance_d | 06-04 | 0 | 695K | 用户财务日 |
| dws_user_promotion_behavior_h | 06-04 | 0 | 152M | 推广行为小时 |
| dws_user_promotion_behavior_charge_h | 06-04 | 0 | 39M | 推广充值小时 |
| dws_user_reg_video_funnel_daily_d | 06-04 | 0 | 492K | 注册视频漏斗日 |
| dws_register_attribution_result_d | 06-03 | 1 | 10K | 归因日批 |
| dws_user_first_recharge_retention_d_h | 06-03 | 1 | 123K | 首充留存 |
| dws_user_promotion_behavior_d | 06-03 | 1 | 102M | 推广行为日 |
| dws_user_promotion_behavior_charge_d | 06-03 | 1 | 36M | 推广充值日 |
| dws_channel_daily_funnel_d | 06-03 | 1 | 2M | 渠道漏斗 |
| dws_user_base_daily_d | 06-03 | 1 | 6K | 用户基础日 |
| dws_video_account_d_d / device_d_d | 06-03 | 1 | 19M/18M | 视频账号/设备 |
| dws_user_ltv_d | 06-03 | 1 | 1 | ⚠️ 旧 LTV，几乎无增量 |
| dws_user_reg_ltv_daily_d_old | 05-28 | 7 | 1.2M | ❌ 弃用 |
| dws_user_first_recharge_retention_d_old | 05-28 | 7 | 13K | ❌ 弃用 |
| dws_user_retention_d | - | - | 0 | ❌ 旧表空 |
| dws_user_reg_video_funnel_d_h | - | - | 0 | ❌ 无数据 |
| dws_keyword_search_conv_d | - | - | 0 | ❌ 无数据 |
| dws_settlement_user_register_h | - | - | 0 | ❌ 无数据 |
| dws_user_tag_d_poc | - | - | 0 | POC |
| 无 dt 16 张 | N/A | - | 有数 | 渠道汇总/结算/MV 源等 |

---

## 三、ADS 全表清单

| 表 | MAX(dt) | 落后 | 近7d行数 | 血缘角色 / 备注 |
|----|---------|:----:|---------:|-----------------|
| ads_app_metrics_daily_d | 06-04 | 0 | 5K | 实时日指标 |
| ads_app_metrics_hourly_d | 06-04 | 0 | 117K | 实时小时 |
| ads_product_day_stat_d | 06-04 | 0 | 6K | **项目日报** |
| ads_channel_metrics_daily_d | 06-04 | 0 | 1.1M | 渠道日指标 |
| ads_ad_click_user_daily_d | 06-04 | 0 | 944K | 广告点击用户日 |
| ads_action_page_funnel_d | 06-04 | 0 | 564K | 页面漏斗 |
| ads_user_page_path_d / name_d_d | 06-04 | 0 | 14M+ | 页面路径 |
| ads_channel_daily_funnel_report_d | 06-03 | 1 | 1.1M | 渠道漏斗日报 |
| ads_page_heatmap_d | 06-03 | 1 | 367M | 页面热点 |
| ads_user_dormancy_d | 06-03 | 1 | 11K | 休眠用户 |
| ads_user_retention_d | MV | - | 7.5M 行 | 源：dws_app_retention_d_h |
| ads_app_video_funnel_d 等 7 张 | - | - | 0 | ❌ 空/停更 |
| 无 dt 12 张 | N/A | - | 有数 | 渠道/广告汇总等 |

---

## 四、异常与建议（结合 memory）

| 优先级 | 项 | 建议 |
|--------|-----|------|
| P1 | dws_app_order_d_h BE rpc（06-04 02:12） | 核对失败 slot 并补跑 |
| P2 | 落地页 DWD 仍 06-03 | 归因/渠道推广日批保持 T+1，今日 06-04 注册明日归因 |
| P2 | 弃用表 old/空表 | 报表勿引用 `dws_user_reg_ltv_daily_d_old`、`dws_user_retention_d` |
| P3 | dws_user_ltv_d 仅 1 行 | 已迁移至 reg_ltv 体系，可下线调度 |

---

*关联：lineage_playbook POC 表清单；lesson 20260603-prod-ltv-backfill、20260603-attribution-analyze-by-app*
