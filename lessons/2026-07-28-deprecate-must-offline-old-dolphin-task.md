---
date: 2026-07-28
tags: [dolphin, deprecate, half-migration, session_duration, test]
severity: high
domain: ops
---

# 合表/废弃表必须同批下线旧海豚 task

## 背景

五档合表 v2（`dev-20260721-002`）把 `dws_session_daily_{user,device}_d` 并进 `dws_session_duration_*_d`（`stat_grain`），test 已 DROP 旧表并发布合表 ETL。但 `wf_dws_汇总_日` 里旧 task 仍 ONLINE → 调度报 `Table … is not found`，连累 ads 日报 / 行为评分 DEPENDENT。

## 坑 / 错误做法

- 只发新 task SQL + migrate DROP 旧表，**不删/不停**旧海豚 task
- README 写「deprecated / 待下线」却不当天清掉调度
- 合表验收只看手动 PI SUCCESS，漏查次日 schedule 05:20

## 正确做法

1. 合表/改名/废弃：**同一变更窗口**内完成  
   - 新表 DDL + 新 ETL 上 test  
   - **DELETE** 旧 task（test：`POST .../tasks/{code}/delete` + `session_code`）  
   - 确认 DAG 边去掉旧节点，下游不误等  
2. 验收：次日 schedule 或补跑整 wf，确认旧名不再出现在 task list  
3. 文档「待下线」= **未完成**，禁止标交付

## 验证

- 2026-07-28 test 已删 `22357870925056` / `22357871175296`；wf 剩 `duration_user/device`；release ONLINE

## 关联

- session：`dev-20260721-002`
- wf：`wf_dws_汇总_日` / `21869820140416`
- 文件：`ops_system/04.dws/dws_session_duration_d/task_daily_*.yaml`
