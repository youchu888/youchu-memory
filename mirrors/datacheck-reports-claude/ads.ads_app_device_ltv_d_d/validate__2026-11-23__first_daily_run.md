# 设备 LTV · 测试日批首跑核验（dt=2026-11-23）

环境：test SR `ads.ads_app_device_ltv_d_d`  
编排：`g_device_daily` 03 槽（测试编排 v40，挂步于 11-23）  
查询时间：2026-11-24

## 结论

**PASS（首跑有数）**。北京时间 2026-11-24 03:46 左右写出 T-1 分区，非手插样例量级。

## 分区概况（近 5 日）

| dt | rows | apps | sum(new_device_cnt) | sum(day_0_pay_amount) | max(etl_update_time) |
|----|------|------|---------------------|------------------------|----------------------|
| 2026-11-23 | 5344 | 424 | 120465 | 11000 | 2026-11-24 03:46:24 |
| 2026-11-22 | 19147 | 475 | 0 | 0 | 2026-11-24 03:46:24 |
| 2026-11-21 | 6635 | 447 | 0 | 0 | 2026-11-24 03:46:24 |
| 2026-11-20 | 10975 | 477 | 0 | 0 | 2026-11-24 03:46:24 |
| 2026-11-19 | 9619 | 479 | 0 | 0 | 2026-11-24 03:46:24 |

说明：按约定**不补历史**；T-1 有新增设备与当日充值，历史分区 `new_device_cnt=0` 属首跑只写当天队列的预期表现（partial-update 链后续日批再填）。

## SR / pay_gap

- test SR 仅有 `ads_app_device_ltv_d_d`（回写步 `pb_ads_app_device_ltv_d_d`）。
- `ads_app_device_ltv_pay_gap_d` **不在 SR**：编排无人读、不回写 SR —— 与挂步回执一致，属有意设计。

## 仍欠

1. 会话 `step.json` 的 `tagTargets` 需补上 `paimon.ads.ads_app_device_ltv_pay_gap_d`（SQL 双写，锚点目前只声明了明细表）。本机仓库无该会话源码（平台会话属其他账号 / 旧机未同步），需旧机或持有会话的环境改完再 push。
2. 生产编排仍不挂。

## SQL

```sql
SELECT dt, COUNT(*) AS rows_n, COUNT(DISTINCT app_id) AS apps,
       SUM(COALESCE(new_device_cnt,0)) AS new_dev,
       SUM(COALESCE(day_0_pay_amount,0)) AS d0_pay,
       MAX(etl_update_time) AS max_etl
FROM ads.ads_app_device_ltv_d_d
WHERE dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)
GROUP BY dt ORDER BY dt DESC;
```
