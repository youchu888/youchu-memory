---
date: 2026-10-21
tags: [ads_channel_promotion_summary_m, ads_channel_promotion_summary_w, publish, test-sync-prod, dept_code, bus10874]
severity: high
domain: ops
source: worker_ant bus#10874
---

# 渠道推广周/月：禁止「测试同步生产」单推未发版 SQL

## 背景

2026-10-20 12:09 野花用「测试同步生产」把 `ads_channel_promotion_summary_m/_w` 换成会话 `dev-20261016-016` 新版（含 `dept_code` 等），但会话仍在 S5、生产 SR 未加列。10-21 07:30 日报表 `Unknown column dept_code`，连带约 20 个 task 未跑。狂人已回滚两 task 到 10-09 版并补数。

## 坑 / 错误做法

- 会话未走完 S6/S7 发布，就用「测试同步生产」单独推 SQL 到生产海豚
- 生产表结构未随发布 ALTER，ETL 先引用新列

## 正确做法

1. 新版上生产必须走完会话 S6/S7 正式发布
2. 生产表改结构与 SQL 发布同一批次完成
3. 禁止再用「测试同步生产」对这两张表（及同类）单推未发版 SQL
4. 现网 prod 已回滚到 10-09 可跑通版本；补数由狂人侧进行中

## 关联

- bus#10874
- session `dev-20261016-016`（月，S5 in_progress）；海豚侧周/月另见 `dev-20260929-001/002`
