---
date: 2026-10-21
tags: [dim_channel_info_all, bmp, prod, audit, bus10911]
severity: high
domain: ops
source: worker_ant bus#10911
---

# prod dim_channel_info_all 空：业务后台只写 test

## 背景

prod SR 表 2026-10-08 21:10 建表后一直 0 行；部门周/月 INNER JOIN 空跑。

## 根因

- test 审计：`172.31.9.165` 每日 **01:30** `INSERT INTO dim.dim_channel_info_all`（业务后台/bmp）
- prod 审计：自建表起 **无任何** `INSERT INTO dim.dim_channel_info_all`（仅 CREATE）
- 不是海豚/Snap ETL 问题；写入任务未配置生产 SR

## 正确做法

1. 业务后台把同一同步任务加上 prod SR 目标（或手动触发）
2. 配置生效后预计次日 01:30 有数；可当天手工跑则当天有数
3. 勿用 test 的 24 行样例当 prod 全量（含测试脏数据）
4. 历史日全量用 Paimon `dim_channel_info_all_snap`（`snap_dt`），runner 下 DATETIME 不减 8h

## 关联

- bus#10911 / #10880
- commit `4b08bd1c`（去减 8h）
