---
date: 2026-05-25
tags: [dolphin, prod, deploy, ltv, first_recharge]
severity: high
domain: ops
---

# 生产海豚：项目 / 工作流 / task code（与 test 不同）

## 背景

发布 5.1.3 `dws_user_reg_ltv_d_h`、5.1.5 `dws_user_first_recharge_retention_d_h` 到**正式**海豚。

## 坑 / 错误做法

- 照搬 test 的 `project_code` / `task_code`（test PC=`20524869250304`）。
- 以为日批 SQL 已发布即可：prod **小时**任务曾为 `flag=NO`（`dws_user_reg_ltv_daily_d_h_7n3` 等），未启用则只有日批无小时增量。

## 正确做法

| 环境 | project_code | dws 小时（prod UI legacy） | 日汇总 DWS canonical |
|------|--------------|---------------------------|----------------------|
| test | 20524869250304 | wf_用户活跃留存_小时 等 | **wf_dws_汇总_日** 21869820140416 |
| **prod** | **20524837077760** | **dws_小时** 21284117013504 | **wf_dws_汇总_日** 20691538136576（UI：`dws_日`） |

对照：`.claude/dolphin/wf_cross_env_map.yaml`

**prod 任务 code（2026-05-25 核实）**

| 模型 | 小时 task | 日批 task |
|------|-----------|-----------|
| reg_ltv_d_h | 21570101162496 | 21196490850432 |
| first_recharge_retention_d_h | 21570126960000 | 21196490850433 |

发布脚本：`dolphin_ops/scripts/deploy_retention_ltv_prod.py`（发布前 `safe-window`，threshold 10min）。

依赖：日批首充 `pre` = `21497544336640`（`dws_app_user_d_h`）；LTV 日批 `pre` = `20691491972736`（`dwd`）。

## 验证

```bash
python3 -m dolphin_ops.cli workflow-show --env prod --project-code 20524837077760 --wf-code 20691538136576
# 目标 task flag=YES，SQL 头注释含 _h 表名
```

## 关联

- 配置：`.claude/dolphinscheduler.json`
- test 部署：`dolphin_ops/scripts/deploy_retention_ltv_test.py`
