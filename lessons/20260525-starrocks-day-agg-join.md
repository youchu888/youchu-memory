---
date: 2026-05-25
tags: [starrocks, datacheck, sql, ltv]
severity: medium
domain: datacheck
---

# StarRocks：日汇总对账用子查询 JOIN，勿 GROUP BY + 相关子查询

## 背景

对比 `dws_user_reg_ltv_d_h` 与旧表 `dws_user_reg_ltv_daily_d` 的 `new_users` 日汇总。

## 坑 / 错误做法

```sql
SELECT h.dt, SUM(BITMAP_COUNT(h.new_users)) h_new,
       (SELECT SUM(o.new_users) FROM old o WHERE o.dt = h.dt) o_new
FROM _h h
GROUP BY h.dt;  -- ERROR: 相关子查询必须出现在聚合或 GROUP BY
```

五维 JOIN 后直接 `SUM(o.new_users)` 且 `_h` 行数多于旧表时，会**重复放大**旧表指标（百万级假 diff）。

## 正确做法

**日汇总：两侧先按 dt 聚合，再 JOIN**

```sql
SELECT h.dt, h.h_new, o.o_new, h.h_new - o.o_new AS diff
FROM (
  SELECT dt, SUM(BITMAP_COUNT(new_users)) AS h_new
  FROM dws.dws_user_reg_ltv_d_h WHERE dt BETWEEN ... GROUP BY dt
) h
JOIN (
  SELECT dt, SUM(new_users) AS o_new
  FROM dws.dws_user_reg_ltv_daily_d WHERE dt BETWEEN ... GROUP BY dt
) o ON h.dt = o.dt;
```

**金额**：`_h` 的 `day_N_pay_amount` 为**元**；旧表常为**分**，对比时 `SUM(old)/100`。

**维度 grain diff**：`BITMAP_COUNT(h.new_users) <> o.new_users` 行数多 ≠ 日总量错，看日 SUM。

## 验证

5 月主验证窗：多数日 `new_users` diff ≤7；`day_0` 元单位一致。

## 关联

- `ops_system/04.dws/dws_user_reg_ltv_d_h/datacheck.sql`
- 报告：`.claude/database/reports/test_ltv_first_recharge_datacheck_20260525.md`
