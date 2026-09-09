---
date: 2026-09-09
tags: [datacheck, dim_user_all, dws_app_user_d, new_users, caliber, agent-bus]
severity: high
domain: datacheck
---

# 新增账号权威源是 dim.register_time；app_user.new_users 少算先拆调度/落表

## 背景

bus#8295：知秋铁律推论权威源=`dim_user_all.register_time`；否 dw 未清洗层、否两套口径并存；`dws_app_user_d.new_users` 的 47,870 不能当基准。

## 坑 / 错误做法

- 把 dim 与 `app_user_d.new_users` 当成同一套「用户活跃口径」
- 见 dwd_v2 < dw 就当缺口（多为 `_r` 清洗设计）
- 未拆清就改 ETL / 双口径改名

## 正确做法

1. 基准：`DATE(dim.register_time)=当天`（app 粒度）。
2. 拆差：A=dim 当日注册 uid；B=按 ETL（PV∪REGISTER 且 dim 当日注册）重算；看 A−B 有无事件。
3. 若 A 全有 REGISTER 但落表仍少：查小时窗是否只到 23:30、**次日 daily OVERWRITE 是否写入该分区**（看 `MAX(update_time)`），勿先判命名问题。
4. 对账用 `BITMAP_UNION_COUNT`，慎用跨维 `SUM(BITMAP_COUNT)`（维值漂移会虚高）。

## 验证

test · YC-001 · 2026-09-04：A=B 重算=52939；落表 SUM=47870；`MAX(update_time)=当日 23:30`（缺 daily）；≥23:30 首注 2713。

## 关联

- 报告：`.claude/database/reports/dws.dws_app_user_d/validate__2026-09-04__new_users_vs_dim_YC-001.md`
- ETL：`ops_system/04.dws/dws_app_user_active/dws_app_user_d_h/`
