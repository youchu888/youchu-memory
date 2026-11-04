# 产品/部门推广周表 · 取数改结算序列 · 10-26 周新旧对比（bus#12320）

- 业务周：`week_start_dt=2026-10-26`（周日 2026-11-01）；对比锚点 `biz_dt=2026-11-01`
- 旧：现网 `ads.ads_*_promotion_summary_w`（源 ads_channel_metrics_daily_d）
- 新：按知秋 11-04 口径用结算 `dws_app_channel_summary_d_d` + 运营留存/活跃重算（未落表，只读对比）
- SQL 改动路径：
  - `ops_system/spark_migrate/ads_product_promotion_summary_w/ads_product_promotion_summary_w.sql`
  - `ops_system/spark_migrate/ads_dept_promotion_summary_w/ads_dept_promotion_summary_w.sql`
  - `ops_system/05.ads/ads_product_promotion_summary_w/ads_product_promotion_summary_w.sql`
  - `ops_system/05.ads/ads_dept_promotion_summary_w/ads_dept_promotion_summary_w.sql`
- **未发布 / 未改海豚**；等审过再上

## 产品周 ads_product_promotion_summary_w

| 口径 | 行数 | week_new_user_num | week_recharge_amt | week_retention_user_num | week_avg_dau |
|------|------|-------------------|-------------------|-------------------------|--------------|
| old  | 478  | 14,356,123        | 1,867,809,489     | 1,669,596               | 6,170,288    |
| new  | 477  | 14,422,979        | 1,883,710,244     | 1,666,721               | 6,280,510    |
| Δ    | -1   | +66,856 (+0.47%)  | +15,900,755 (+0.85%) | -2,875 (-0.17%)      | +110,222 (+1.79%) |

新增/充值差属换结算源预期；次留/日活改运营 bitmap，总量接近。

## 部门周 ads_dept_promotion_summary_w

| 口径 | 行数 | week_new_user_num | week_recharge_amt | week_retention_user_num | week_avg_dau |
|------|------|-------------------|-------------------|-------------------------|--------------|
| old  | 63,369 | 14,854,094      | 1,937,346,158     | 1,731,204               | 7,340,708    |
| new  | 63,172 | 14,935,961      | 1,954,454,113     | 1,728,198               | 7,381,981    |
| Δ    | -197 | +81,867 (+0.55%)  | +17,107,955 (+0.88%) | -3,006 (-0.17%)      | +41,273 (+0.56%) |

## 产品周 · 新增差绝对值 Top（抽样）

| dept_id | app_id | old_nu | new_nu | Δnu | old_amt | new_amt | Δamt |
|---------|--------|--------|--------|-----|---------|---------|------|
| 93 | HX-001 | 749324 | 767041 | -17717 | 5167500 | 5288500 | -121000 |
| 73 | JHA-157 | 115490 | 127170 | -11680 | 1022000 | 1037000 | -15000 |
| 93 | HX-003 | 173429 | 183200 | -9771 | 1294000 | 1345000 | -51000 |
| 89 | DX-092 | 11365 | 19342 | -7977 | 3740000 | 4950000 | -1210000 |

## 实现要点（对照知秋）

1. 周新增 = SUM(`dws_app_channel_summary_d_d.new_user`)，不做 bitmap 去重
2. 周充值 = CAST(SUM(`recharge_amount`) AS BIGINT)，**不加** `coin_recharge_amount`
3. 周次留 = 注册日∈[周一, min(周日,业务日-1)]，渠道日 `day1_ret_cnt` 计数后按部门×产品 / 渠道×部门相加
4. 周日均活跃 = 天级合并 `active_users` 计数后 AVG（有数天）
5. 分组/周界/部门维/paid_type/产品推广窗：保持原逻辑
6. SR 稿次留/日活读 `dws.dws_app_*`（Paimon 回写，bitmap 原生）；Spark 稿读 `paimon.dws.*` + `bm_*`
