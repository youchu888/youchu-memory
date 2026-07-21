---
date: 2026-06-29
tags: [dolphin, sql, attribution, prod, datacheck]
severity: high
domain: ops
---

# 海豚 SQL 块注释导致 INSERT 0 行仍 SUCCESS

## 背景
`dws_register_attribution_metrics_d_d` prod 补数实例全 SUCCESS，但表 0 行。

## 坑 / 错误做法
ETL 文件以 `/* ... */` 块注释开头，紧跟 `INSERT OVERWRITE ...`。海豚 JDBC 执行后任务 SUCCESS，StarRocks 实际 0 行写入。

## 正确做法
1. **可执行 INSERT/UPDATE ETL**：文件头只用 `--` 行注释，不用块注释包 header。
2. DDL 单独 task 可保留块注释（deploy 脚本 strip 后执行）。
3. 发布后核验：`SELECT COUNT(*) FROM 目标表 WHERE dt=T-1`，不能只看海豚 SUCCESS。

## 验证
```sql
SELECT dt, COUNT(*) FROM dws.dws_register_attribution_metrics_d_d WHERE dt = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) GROUP BY dt;
```

## 关联
- `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/dws_register_attribution_metrics_d_d.sql`
- `dolphin_ops/scripts/deploy_attribution_prod.py`
