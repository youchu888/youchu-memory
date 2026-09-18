# Playbook 核查报告：dws.dws_register_attribution_metrics_d_d

**Session**: dev-20260624-001  
**环境**: test (`starrocks.test` / `my.cnf.test`)  
**业务日 T-1**: 2026-06-23  
**执行时间**: 2026-06-24  
**剧本**: `dws_register_attribution_metrics_d_d/playbook.md`

## 汇总

| 检查点 | 结果 | 说明 |
|--------|------|------|
| part_01 分区存在 | ❌ BLOCK | 表未建；剧本 SQL 在 SR 上 `PartitionName >=` 语法也不支持 |
| part_02 T-1 有数据 | ❌ BLOCK | 目标表不存在 |
| part_03 比率自洽 | ⏭ SKIP | 目标表不存在 |
| part_04 明细对账 | ⏭ SKIP | 目标表不存在 |
| part_05 DWD 对账 | ⏭ SKIP | 目标表不存在 |
| part_06 影子期写回 | ⏭ SKIP | 目标表不存在 |
| part_07 主键唯一 | ⏭ SKIP | 目标表不存在 |

**结论**：Stage 4 前置未满足 — **须先在 test 跑 DDL 建表，再跑 ETL**。test 上游表 T-1 亦无数据，ETL 跑通后 part_02 可能仍为空行（需补上游或换有数日期）。

## 逐条明细

### part_01 分区存在

- **期望**：含 2025-12-20 起分区
- **实际**：
  ```
  Table dws_register_attribution_metrics_d_d is not found.
  ```
- **剧本 SQL 问题**：`SHOW PARTITIONS ... WHERE PartitionName >= 'p20251220'` 在 StarRocks 报错：`Only operator =|like are supported for PartitionName`；`LIKE` 子句亦不支持
- **建议 SQL**：
  ```sql
  SHOW PARTITIONS FROM dws.dws_register_attribution_metrics_d_d;
  ```
  人工确认列表中含 `p20251220` 及以后分区

### part_02 T-1 有数据

- **期望**：白名单 app 有行
- **实际**：表不存在，未执行
- **附注**：test 环境 `dws.dws_register_attribution_result_d` T-1 **0 行**；`dwd.dwd_user_register_d_v2` iOS organic flag=1 T-1 **0 行**（全表空）
- **prod 对照**（只读）：结果表最近 `dt=2026-06-22` 有 39 行 — 上线后应在 prod 补数验证

### part_03～part_07

目标表不存在，跳过。DDL + ETL 落 test 后重跑。

## 下一步（Stage 4）

1. Stage 4 面板先跑 **`dws_register_attribution_metrics_d_d_ddl.sql`**
2. 再跑 **`dws_register_attribution_metrics_d_d.sql`**（已改为 `$[yyyyMMdd-1]` / `'$[yyyy-MM-dd-1]'` 内联宏）
3. 重跑本 playbook-check
4. 若 test 上游无 T-1 数据：用 complement 补归因链路，或临时将检查 SQL 中 `DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)` 改为 prod 有数日（如 `2026-06-22`）做 dry-run 对账

## 变更记录

- 2026-06-24 又初：dev-20260624-001 stage4 playbook-check 首跑
