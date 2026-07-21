---
date: 2026-05-26
tags: [dolphin, complement, partition, prod]
severity: high
domain: ops
---

# 海豚日批补数：schedule 日 ≠ cohort 日

## 背景

生产补数 `dws_user_reg_ltv_d_h` / `dws_user_first_recharge_retention_d_h`，业务要求 cohort `dt` 从 2025-12-20 到 2026-05-26。

## 坑 / 错误做法

1. `complement --start 2025-12-20` → 写入分区 `p20251219`，分区不存在 → **FAILURE**。
2. `complement --start 2026-04-26`（已有 p20260426）→ 写入 `p20260425` → **FAILURE**。
3. 同一 **`wf_dws_汇总_日`** wf（prod 20691538136576）在 LTV 补数未完成时再提交首充补数 → 两条 SERIAL 链交错（见 complement-serial lesson）。

## 正确做法

| 目标 cohort dt | complement scheduleTime（start/end） |
|----------------|--------------------------------------|
| 2025-12-20 | 2025-12-21 00:00:00 |
| 2026-04-26 | 2026-04-27 00:00:00 |
| 2026-05-26 | 2026-05-27 00:00:00 |

**已有分区** cohort `2026-04-26`~`2026-05-26`：

```bash
# LTV（TASK_ONLY）
complement --start "2026-04-27 00:00:00" --end "2026-05-27 00:00:00" --start-nodes 21196490850432

# 首充（TASK_POST，须等 LTV 链跑完再提交）
complement --start "2026-04-27 00:00:00" --end "2026-05-27 00:00:00" --start-nodes 21196490850433
```

**更早 cohort**（`2025-12-20`~`2026-04-25`）：先 admin 执行
`.claude/database/reports/prod_ltv_fr_backfill_partitions_admin_20260526.sql`，再：

```bash
complement --start "2025-12-21 00:00:00" --end "2026-04-26 00:00:00" ...
```

## 验证

- 海豚：目标 schedule 段内 complement 全 SUCCESS。
- 库：`MIN(dt)`/`MAX(dt)` 覆盖目标 cohort；`COUNT(DISTINCT dt)` = 天数。

## 关联

- admin 分区脚本：`.claude/database/reports/prod_ltv_fr_backfill_partitions_admin_20260526.sql`
