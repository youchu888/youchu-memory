---
title: prod 海豚补数对所有登录用户放开
date: 2026-08-01
tags: [dolphin, complement, prod, ops]
severity: high
---

## 变更（bus#5864 · 知秋钦定）

2026-08-01 起 `dolphin.complement_data` + `env=prod` 对所有登录用户开放；发布/改 SQL 仍 admin。

## 三坑

1. **task_dep_type**：TASK_ONLY 只刷本表；要带下游用 TASK_POST；周/月必须 TASK_PRE
2. **日期**：业务时间 `YYYY-MM-DD HH:MM:SS`；补前 `preview_macros`
3. **force=true**：仍仅 admin

## 验收

SUCCESS 不够，须验表分区有数。

## 关联

- `.claude/memory/reference_prod_complement_open_20260801.md`
- `_dolphin_rules.md` §12
