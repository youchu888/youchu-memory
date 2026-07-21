---
date: 2026-05-26
tags: [api, lineage, dc-platform]
severity: medium
domain: ops
---

# dc-platform lineage API 返回 0 边时的处理

## 背景

补数后用户要求 `GET /api/v1/lineage/{db}/{table}` 查上下游。

## 现象

- HTTP 200，但 `edge_count=0`，`upstream_tables=[]`，`downstream_tables=[]`
- `GET /api/v1/relations/table/...` 同样空
- `GET /api/v1/tables/dws.xxx` 有列元数据（表已在 OM）

## 正确做法

1. 仍调用 lineage + relations + tables API 并记录结果。
2. **兜底**：读 `ops_system/04.dws/{table_dir}/*.md` 与 `*_daily.sql` 注释中的数据源。
3. 告知用户：需在平台做血缘同步后 API 才有边；设计口径见报告。

## 设计口径（本仓库两张表）

- `dws_user_reg_ltv_d_h`：`dim.dim_user_all` + `dwd.dwd_order_paid_d`
- `dws_user_first_recharge_retention_d_h`：`dim.dim_user_all` + `dws.dws_app_user_d_h`

## 关联

- 配置：`.claude/database/dc-platform.json`
- 报告：`.claude/database/reports/prod_ltv_fr_backfill_validation_20260526.md`
