---
date: 2026-06-09
tags: [attribution, dwd, dolphin, test, schema]
severity: high
domain: ops
---

# dwd_user_register_d_v2 attribution_flag 列错位

## 现象
测试库 `attribution_flag` 全是 `1248474xxx` 整数，`etl_time` 为 NULL；源表 payload 解析应为 0/NULL。

## 根因
测试表 `ALTER ADD attribution_flag` 后物理列序为 `trace_id, etl_time, attribution_flag`，而 ETL SELECT 按仓库 DDL 顺序 `trace_id, attribution_flag, etl_time` 做**按位 INSERT**，`CURRENT_TIMESTAMP()` 被 CAST 进 `attribution_flag`。

小时任务 `wf_用户画像_小时` / `174729503687488` 曾缺 `attribution_flag` 字段，日批补数后仍会被小时 upsert 污染。

## 正确做法
1. **INSERT 必须写显式列名**（daily + hourly）：
   `(dt, ..., trace_id, attribution_flag, etl_time) SELECT ...`
2. 发布两个海豚任务：日 `wf_dwd_事件明细_日` `174729506942789`、小时 `wf_用户画像_小时` `174729503687488`。
3. 补数后核验：
   ```sql
   SELECT attribution_flag, COUNT(*), MAX(etl_time)
   FROM dwd.dwd_user_register_d_v2 WHERE dt='2026-06-02' GROUP BY 1;
   ```
   应见 0/NULL 分布且 `etl_time` 非空。

## 后续踩坑（2026-06-10 补充）
- REST 发布走 OFFLINE→PUT→ONLINE 会把 **schedule 打成 OFFLINE**，且 wf 重新 ONLINE 后调度不会自动恢复。
- 后果：`wf_用户画像_小时` 停摆一夜，注册表断流（6/9 20:03 后无数据），日批 6/10 凌晨也未跑。
- **发布后必须核验 schedule releaseState 并 `POST /schedules/{id}/online`**。
- 修复：schedule 96/100/103 复位 ONLINE；补数业务日 6/9；手工 OVERWRITE p20260610 补当日缺口。

## 关联
- `ops_system/02.dwd/.../dwd_user_register_d_v2_daily.sql`
- `ops_system/02.dwd/.../dwd_user_register_d_v2_hourly.sql`
