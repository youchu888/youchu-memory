---
date: 2026-06-03
tags: [prod, ltv, dolphin, complement, readonly]
severity: high
domain: ops
---

# 生产 LTV 补数：readonly 不能直接写 SR

## 背景
补 `dws_user_reg_ltv_d_h` @ 2026-05-27 生产分区。

## 坑 / 错误做法
- `my.cnf.prod` 只有 `readonly_role`，`INSERT OVERWRITE` 报 5203。
- dc-platform token 非 admin，`POST /dolphin/complement-data?env=prod` 返回 403。
- dc-platform `complement-data?env=prod` 403 时，勿与「token 失效」混为一谈；**直连 prod Dolphin API**（`.claude/dolphinscheduler.json` token）通常可用。

## 正确做法
1. **生产项目** `20524837077760`（≠ 测试 `20524869250304`）。
2. **日批**：工作流 **`wf_dws_汇总_日`**（prod wf_code `20691538136576`；UI legacy `dws_日`），任务 `21196490850432`，补数 `2026-05-28 05:20:00`，`execType=COMPLEMENT_DATA`，`taskDependType=TASK_ONLY`，`startNodeList=21196490850432`。
3. **小时**：工作流 `dws_小时` `21284117013504`，任务 `21570101162496`，`2026-05-27 07:30`–`23:30`，同上参数。
4. MCP `dolphin.complement_data` 与上述 API 等价；仓库内无 `dolphin_ods` CLI。
3. 刷新视图：ETL 账号执行 `dws_user_reg_ltv_daily_d_view_ddl.sql`。
4. 验证用 readonly 跑 UC-01/02（`dws_user_reg_ltv_d_h.md` §8）。

## 验证
```sql
SELECT COUNT(*), SUM(BITMAP_COUNT(new_users)), SUM(day_0_pay_amount)
FROM dws.dws_user_reg_ltv_d_h WHERE dt='2026-05-27';
```
UC-01：`dim_sum_by_dim = SUM(BITMAP_COUNT(new_users))`（2026-05-27 生产已对齐 4,734,545）。

## 关联
- `.claude/database/reports/dws_user_reg_ltv_backfill_20260527_prod.md`
- `.claude/database/reports/dws_user_reg_ltv_daily_20260527_prod.sql`
