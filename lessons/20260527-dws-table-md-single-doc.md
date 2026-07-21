---
date: 2026-05-27
tags: [sql, datacheck, docs, dws, ops]
severity: high
domain: ops
---

# DWS 模型文档统一为 `{table}.md`（含代码 + 对账）

## 背景

`dws_user_reg_ltv_d_h`、`dws_user_first_recharge_retention_d_h` 等小时+日批模型，原先设计说明、ETL、对账分散在 `*_design.md`、独立 `datacheck.sql`、报告里，改 SQL 容易漏改文档。

## 坑 / 错误做法

- 单独维护 `datacheck.sql`，与 `tablename.md` 双份来源，很快漂移。
- **只对 `_old` / 旧物理兼容表做对比** → 无法证明口径与 ETL 正确，迁移完就失效。
- 用 `COUNT(DISTINCT uid)` 全表对比 `SUM(BITMAP_COUNT)` → dim 同 uid 多维度行时会误判失败（应对齐 ETL 维度 GROUP BY 后汇总）。
- 对账 SQL 在 WHERE 里直接写 `h.day1_ret_cnt IS NULL`（BITMAP 列）→ StarRocks 报错。
- 生产未执行兼容视图 DDL 时，仍用「视图 vs _h」作主判据 → 百万级 `diff_rows`，误判为 ETL 坏了。
- `*_old` 备份表不存在的环境仍跑旧表对比 → `Unknown table`。

## 正确做法

每个模型目录 **只保留一个权威文档**：

```text
ops_system/04.dws/{table}/
  {table}.md              # 设计 + 全部 SQL 代码块 + 对账（第 8 节）
  {table}_ddl.sql
  {table}_hourly.sql
  {table}_daily.sql
  {table}_view_ddl.sql
  # 无 datacheck.sql
```

`{table}.md` 结构：

1. 口径 / 依赖 / hourly vs daily / 调度
2. **§8 对账**（分层，**主**为上下游）：
   - **UC-xx**：按 `*_daily.sql` 从 §2 源表重算（dim + dwd/dws_app_user），与 `_h` 比对
   - **IQ-xx**：本表逻辑自检（脏数据、分区）
   - **VW-xx**：兼容视图 vs `_h`、未成熟窗（须 `table_type=VIEW`）
   - **REF-xx**：`_old` / 旧物理表，**仅参考**
3. 文件清单 + 各 `.sql` 全文嵌入（改 SQL 必须同步改对应代码块）

§8 每条 = SQL + 通过标准 + 实测表 + ✅/⚠️/❌；校验日占位 `@{chk_dt}`（建议 T-2 已闭窗 cohort）。

对账结论标记：

| 标记 | 含义 |
|------|------|
| ✅ 通过 | 满足通过标准 |
| ⚠️ 待办/跳过 | 前置未满足（如视图未上线、无 _old 表）或需重跑 |
| ❌ 异常 | 违反通过标准，需修 ETL 或数据 |

BITMAP 对账写法：用子查询先 `BITMAP_COUNT` 再比较标量，勿在 WHERE 里谓词 BITMAP。

上线兼容视图前：先查 `information_schema.tables.table_type`，`daily_d` 须为 `VIEW` 再跑 DC-01/02/03。

## 验证

- 目录下无 `datacheck.sql`、无 `*_design.md`
- `{table}.md` 含 §8 且标注最近执行日期
- 改 `*_hourly.sql` 后 diff 同步更新 md 内代码块

## 补充（同日）

- **AGGREGATE DECIMAL SUM**：DDL **不要** `DEFAULT "0"`（见 `feedback_starrocks_default_value_caution`）；hourly 无支付行用 `CAST(0 AS DECIMAL(18,4))`。
- **BITMAP hourly**：`BITMAP_UNION` 重复写同 bitmap **幂等**；非幂等的是 reg_ltv 的 `DECIMAL SUM` hourly。
- **首充留存 channel**：`COALESCE(dim_user.channel,'organic')`，不用 `register_channel`；与 `dws_app_user_d_h` strict-channel 对齐。
- **分区 DDL**：静态 `END` 宜略超前（如 `2026-06-01`），避免运维误以为未续；`dynamic_partition.end` 仍负责滚动。

## 关联

- `ops_system/04.dws/dws_user_reg_ltv_d_h/dws_user_reg_ltv_d_h.md`
- `ops_system/04.dws/dws_user_first_recharge_retention_d_h/dws_user_first_recharge_retention_d_h.md`
- `.claude/database/reports/prod_ltv_fr_backfill_validation_20260526.md`
