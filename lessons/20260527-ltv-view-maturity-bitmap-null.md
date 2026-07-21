---
date: 2026-05-27
tags: [starrocks, view, ltv, retention, bitmap, datacheck]
severity: high
domain: sql
---

# LTV/首充 view 未成熟窗 +1 天 & BITMAP ifnull

## 背景

`day_N` 按 `dt <= CURRENT_DATE() - N` 开放时，在 **支付日/活跃日 00:00** 就会把 hourly 累加中的半截子数当「成熟值」给下游；且 daily 只 OVERWRITE **昨日 cohort**，历史 cohort 的 dayN 靠支付日当天 hourly 闭窗。

## 坑

- 报表同一天多次查看 day2「一直在涨」。
- 凌晨下游 ETL 读到 view 非 NULL 残值。
- `BITMAP_AND(cohort_bm, NULL)` → NULL；标量 **`bitmap_union(a,b)`** 任一侧 NULL → NULL。
- 聚合 `BITMAP_UNION(col)` 跳过 NULL；`UNION ALL` 两路合并时一路 NULL 会丢数。

## 正确做法

1. **view 方案 A**：`day_N` 用 `dt <= DATE_SUB(CURRENT_DATE(), INTERVAL (N+1) DAY)`（day_K 同理 `K+1`）。
2. **BITMAP**：参与 **AND/OR/标量 union** 与 **聚合 UNION** 前均 `ifnull(x, bitmap_empty())`；hourly `merged` 最终聚合也要 ifnull。
3. 文档 §5.1 写清时间线；VW-02 对账按新判定（昨日 cohort 的 day_1 应为 NULL）。

## 验证

- 重跑 `*_view_ddl.sql` CREATE OR REPLACE VIEW。
- `CURRENT_DATE=2026-05-27`：cohort 05-25 的 day_2 在 view 中为 NULL；05-28 起非 NULL。

## 关联

- `dws_user_reg_ltv_daily_d_view_ddl.sql`
- `dws_user_first_recharge_retention_d_view_ddl.sql`
- `dws_user_reg_ltv_d_h.md` §5.1
