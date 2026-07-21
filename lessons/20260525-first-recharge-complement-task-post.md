---
date: 2026-05-25
tags: [dolphin, first_recharge, complement, user_d_h]
severity: medium
domain: ops
---

# 首充留存日批补数：TASK_POST + dws_app_user_d_h

## 背景

`dws_user_first_recharge_retention_d_h` 日批活跃来自 `dws_app_user_d_h.active_users`（strict-channel），非 `dwd_app_page_view_d`。

## 坑 / 错误做法

- 仅 `TASK_ONLY` 补首充日批：cohort 有数但 dayN 偏低或缺上游活跃日。
- 未先保证 `user_d_h` 对应日期有分区。

## 正确做法

```bash
python3 -m dolphin_ops.cli complement --env prod \
  --project-code 20524837077760 --wf-code 20691538136576 \
  --start "YYYY-MM-DD 00:00:00" --end "YYYY-MM-DD 00:00:00" \
  --start-nodes 21196490850433 \
  --task-dep TASK_POST \
  --run-mode RUN_MODE_SERIAL
```

prod 日批首充 `pre_task`：`21497544336640`（`dws_app_user_d_h`）。

与旧表对账：cohort 人数可一致，**day1 系统性偏高** 为活跃口径升级（预期，非 bug）。

## 验证

- `SUM(BITMAP_COUNT(first_recharge_users))` 与 dim 首充总量一致。
- 无 `fr=0 AND day1>0` 行。

## 关联

- SQL：`ops_system/04.dws/dws_user_first_recharge_retention_d_h/dws_user_first_recharge_retention_d_h_daily.sql`
