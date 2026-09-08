---
title: 海豚停跑占位禁纯 SELECT 1（sqlType=NON_QUERY 会 executeUpdate 失败）
tags: [dolphin, attribution, stop-placeholder, sqlType, NON_QUERY]
severity: medium
---

# 海豚停跑占位禁纯 SELECT 1

归因升级把 metrics/dashboard_ext 改成 `SELECT 1` 占位后，test 定时整 wf FAILURE。

根因：历史 task `sqlType=1`（NON_QUERY）走 `executeUpdate()`，不能跑 SELECT。

做法：用 `INSERT INTO t SELECT * FROM t WHERE FALSE` 0 行空跑；表若不存在（如 test 无 dashboard_ext）改借已有表。平台 lint 禁 `DELETE FROM`。
