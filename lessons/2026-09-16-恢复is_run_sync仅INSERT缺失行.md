---
date: 2026-09-16
tags: [is_run_sync, attribution, config]
severity: high
domain: ops
---

# 恢复 is_run_sync：仅 INSERT 缺失行

## 背景

前台按配置表查开启归因产品；sync 09-12 停用后入围 app（如 HX-*）无配置行。主人确认恢复写入。

## 正确做法

- 入围与 result 四条件一致（不关联安装）
- `LEFT JOIN` 配置表，`WHERE c.app_id IS NULL` 才 INSERT
- `is_run=1`，`is_active=0`，打分抄 default；**不 UPDATE** 已有行
- test task `22955590456576` v299；09-10 补数 +20，总数 104，重跑无重复

## 关联

- SQL：`ops_system/04.dws/dws.dws_register_attribution_v1011/dim_app_attribution_config_is_run_sync_d.sql`
- 定稿：`is_run定稿-2026-09-11.md`
