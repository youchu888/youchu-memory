---
date: 2026-10-21
tags: [ads_dept_promotion_summary_w, ads_dept_promotion_summary_m, dim_channel_info_all, INNER JOIN, bus10880]
severity: high
domain: ops
source: worker_ant bus#10880
---

# 部门推广周/月空跑：INNER JOIN 空维表 dim_channel_info_all

## 背景

prod `ads.ads_dept_promotion_summary_w/m` 全表 0 行；海豚 task 自约 10-15 起每天 0~1 秒 SUCCESS。

## 根因

ETL 对 `dim.dim_channel_info_all` 做 **INNER JOIN** 取部门。prod 该维表 **COUNT=0** → `daily`/`key_set` 空 → INSERT OVERWRITE 写 0 行仍 SUCCESS。

对照：上游 `ads.ads_channel_metrics_daily_d` T-1 有数十万行；渠道周/月用 **LEFT JOIN** 同维表，故仍有产出。

## 正确做法

1. 先恢复/灌数 prod `dim.dim_channel_info_all`（SR 源表有数）
2. 再补跑 `ads_dept_promotion_summary_w` / `_m`
3. 勿在维表为空时只补跑部门汇总（必空跑）

## 关联

- bus#10880
- 与 `dim_channel_info_all_snap`（SR→Paimon）不同：海豚部门表读的是 **SR 维表本身**
