---
date: 2026-10-23
tags: [spark, srViews, dim_channel_info_all_snap, stage4]
severity: high
domain: ops
---

# 编排挂载步缺 srViews 时 ETL 改读 Paimon snap，勿只靠 step_def

## 背景

管理报表部门周/月、产品周挂 testcluster 后，daemon/`run-step` 按步名跑报 `TABLE_OR_VIEW_NOT_FOUND sr_dim_channel`。`step.json` 虽写了 `srViews`，编排里既有 compute 步未带上；控制面无可靠 replace API。

## 坑 / 错误做法

- 只靠 `step_def` + `srViews` 做 S4，以为挂载步也会有视图
- 产发前不按**挂载步名**冒烟，只验临时 step_def

## 正确做法

1. 渠道维优先读已有日快照：`paimon.dim.dim_channel_info_all_snap WHERE snap_dt='${DT}'`
2. `step.json` 去掉对该维的 `srViews`；probe 加 `dim.dim_channel_info_all_snap` 水位
3. `sql/deploy` 后按**编排步名** `run-step`（env=test）冒烟，确认无 `sr_dim_channel` 报错
4. 产发前提醒：prod snap 无分区时 INNER JOIN 会空表（与 prod SR 渠道维空同源）

## 验证

test 任务日 2026-10-23：`ads_dept_promotion_summary_w/m` rows_out=41；`ads_product_promotion_summary_w`=8；commit `ad004aed`。

## 关联

- 目录：`ops_system/spark_migrate/ads_{dept,product}_promotion_summary_*`
- 会话：`dev-20261022-001/002/003`
