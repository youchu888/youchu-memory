---
date: 2026-07-01
tags: [attribution, dolphin, test, prod, publish, DAG]
severity: high
domain: ops
trigger: 归因发布, test prod 对比, wf_dws_汇总_日
---

# 归因 test DAG 就位后的发布判断

## 背景

bus#652/#706：test 实施归因 A 方案（DAG 归因先行 + SF-81 灰度）。用户问「要不要发布」。

## 坑

1. **test 与 prod task 版本不同步**（test 领先）≠ 一定要再发 test。
2. **prod DAG 顺序与 test 不同**——bus#706 明确 prod **保持旧顺序**，只比对归因链 SQL 版本。
3. **DDL 先于 ETL** 上 prod 会炸（rewrite_status 列，bus#617）。
4. 用户说「可以发 prod」≠ 可以发——须知秋令 + 狂人技术把关（bus#622）。

## 正确做法

### test 要不要发？

```
线上 SQL == repo  &&  DAG 顺序正确  &&  验收已过
→ test 无需再发
```

核对：MCP `dolphin_get_task_sql` env=test，对比 `ops_system/.../*.sql`。

### prod 要不要发？

又初 **禁止自发**。流程：

1. test 验收报告路径贴群
2. @worker_ant_bot 转知秋，列清：发哪些 task、DAG 是否动、是否影子期
3. 等批复后由 admin/知秋侧 publish

### test 常量（2026-07-01 v76）

- wf `21869820140416`，归因链见 `reference_attribution_p0_quickstart.md`
- 脚本：`dc-platform-server/scripts/reorder_wf_attribution_first.py`

### 灰度不开版

扩 app 只 `UPDATE dim_app_attribution_config SET is_rewrite_channel=1`，当晚日批或 TASK_ONLY apply。

## 验证

- `dolphin_get_workflow` test：result → apply → metrics 边存在；app_order 在 metrics 之后
- 群请示已发且 bus 有 outbound 记录

## 关联

- `feedback_prod_release_review_gate.md`
- commit `1a1982f`（DAG reorder scripts）
