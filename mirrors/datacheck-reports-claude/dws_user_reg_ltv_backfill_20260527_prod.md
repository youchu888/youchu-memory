# 生产补数：`dws_user_reg_ltv_d_h` @ 2026-05-27

## 背景

- 生产 `dt=2026-05-27`：`new_users=0`，仅 2694 行 pay 增量（缺 reg_incr）。
- 本地 `my.cnf.prod` 为 **readonly_role**，无法直接 `INSERT OVERWRITE`。
- dc-platform token 无 **prod 海豚** 写权限（403）；生产补数改用 **prod Dolphin REST API** + `.claude/dolphinscheduler.json` token（2026-06-03 已可用）。

## 推荐补数方式（生产海豚 UI / 有效 prod token）

### 方案 A：日批闭窗（推荐，一次修好 cohort）

**生产（已执行 2026-06-03）** 工作流 **`dws_日`** `wf_code=20691538136576`，任务 **`dws_user_reg_ltv_d_h`** `task_code=21196490850432`。

测试参考：工作流 **`wf_dws_汇总_日`** `wf_code=21869820140416`，任务 `task_code=174729603403595`：

| 参数 | 值 |
|------|-----|
| 补数类型 | COMPLEMENT_DATA |
| schedule_start | `2026-05-28 05:20:00`（T+1 日批时刻；会 OVERWRITE `p20260527`） |
| schedule_end | 同上（单日） |
| task | 仅 `dws_user_reg_ltv_d_h` |
| task_dep_type | TASK_ONLY |
| run_mode | RUN_MODE_SERIAL |

> 日批逻辑：`INSERT OVERWRITE PARTITION (p20260527)`，cohort = `DATE(register_time)=2026-05-27`。

已渲染 SQL 见：`/tmp/dws_user_reg_ltv_d_h_daily_20260527_prod.sql`（需 ETL 账号执行）。

### 方案 B：小时链补数（辅助）

**生产（已执行）** 工作流 **`dws_小时`** `wf_code=21284117013504`，任务 `task_code=21570101162496`。

测试参考：工作流 **`wf_用户活跃留存_小时`**，任务 **`dws_user_reg_ltv_d_h`**：

| 参数 | 值 |
|------|-----|
| schedule_start | `2026-05-27 07:30:00` |
| schedule_end | `2026-05-27 23:30:00` |
| startNodeList | `dws_user_reg_ltv_d_h` 的 task_code |
| task_dep_type | TASK_ONLY |
| run_mode | RUN_MODE_SERIAL |

## 验证（readonly 可跑）

```sql
-- 1) 分区概览
SELECT COUNT(*) AS cnt,
       SUM(BITMAP_COUNT(new_users)) AS nu,
       SUM(day_0_pay_amount) AS d0,
       SUM(day_1_pay_amount) AS d1
FROM dws.dws_user_reg_ltv_d_h
WHERE dt = '2026-05-27';

-- 2) UC-01 与 dim 按维汇总
-- （见 dws_user_reg_ltv_d_h.md §8.2，chk_dt='2026-05-27'）
```

通过标准：`nu > 0` 且与 dim 按维 `SUM(COUNT DISTINCT uid)` 一致。

### 2026-06-03 生产验证结果

| 指标 | 值 |
|------|-----|
| 行数 cnt | 1,209,538 |
| `SUM(BITMAP_COUNT(new_users))` | 4,734,545 |
| day_0 | 17,103,341.30 |
| UC-01 dim_sum_by_dim | 4,734,545 = target ✅ |
| 海豚日批 | `dws_日` @ 2026-05-28 05:20 SUCCESS |
| 海豚小时 | `dws_小时` 2026-05-27 07:30–23:30 共 17 槽 SUCCESS |

## 刷新视图

生产 `dws_user_reg_ltv_daily_d` 已是 **VIEW**。用 ETL 账号执行：

`ops_system/04.dws/dws_user_reg_ltv_d_h/dws_user_reg_ltv_daily_d_view_ddl.sql`

```sql
CREATE OR REPLACE VIEW dws.dws_user_reg_ltv_daily_d AS ...
```

## API 示例（需 admin / 有效 prod 海豚 token）

```bash
curl -X POST -H "token: <PROD_DS_TOKEN>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  "http://18.141.232.237:12345/dolphinscheduler/projects/20524869250304/executors/start-process-instance" \
  -d "processDefinitionCode=<WF_CODE>" \
  -d 'scheduleTime={"complementStartDate":"2026-05-28 03:00:00","complementEndDate":"2026-05-28 03:00:00"}' \
  -d "execType=COMPLEMENT_DATA" \
  -d "runMode=RUN_MODE_SERIAL" \
  -d "taskDependType=TASK_ONLY" \
  -d "startNodeList=<LTV_TASK_CODE>"
```
