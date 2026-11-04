---
date: 2026-11-04
tags: [fanout, bucket, prod, spark, page-item-ctr, sizing]
severity: high
domain: ops
---

# 产发前必须探 prod 量级定 bucket/并行度，禁止用 test 数

## 背景

点击率 `dwd_app_pageitem_d_r` fanout 草稿曾写 bucket=1（按 test 单日约 6.4 万行）。狂人打回：prod 量级差数百倍，bucket 建表后不可改，定错只能删表重建。

## 坑 / 错误做法

- 用 **test 跑数行数** 估 fanout `bucket` / `sinkParallelism`
- 盲抄「建议值」却不查当日 prod 宽表/同量级表
- 未对照现网同类表（如 `dwd_app_page_view_d_r`、`dwd_app_page_click_d_r`）的 bucket 配置

## 正确做法

1. **发生产 / 合 fanout / 建 paimon `_r` 之前**，先在 **prod** 探数：
   - 事件日量：`paimon.dw.dw_user_event_detail_new`（或对应上游）按 `dt=T-1`、目标 `event` 做 `COUNT(*)`
   - 对照同量级已上线 fanout 表的 `bucket` / `sinkParallelism`（`data-load-paimon-s3/.../fanout/manifest.json`）
2. 按 **prod 量级** 写进：fanout 草稿、`*_paimon_ddl.sql`、`design.md`（三处一致）
3. 在 commit / 提审说明里写清：探的哪天、多少行、为何取该 bucket
4. test 数字只用于功能验收，**禁止**写入产发配置

## 验证（本例 2026-11-03）

| 事件 | prod 行数 | 现网对照 |
|------|-----------|----------|
| app_pageitem_exposure | 80,446,332 | — |
| app_pageitem_click | 6,912,631 | — |
| app_page_view（对照） | ≈6.67 亿 | bucket=32 / par=16 |
| page_click（对照） | ≈27 亿 | bucket=64 / par=64 |

pageitem 合计 ≈8736 万/天 → 取 **bucket=16 / sinkParallelism=8**（commit `44018424`）。

## 关联

- 会话：`dev-20261020-002` · `ops_system/spark_migrate/ads_page_item_ctr_d/`
- bus：#12298 打回 → #12301 回执
- feedback：`feedback_prod_bucket_from_prod_probe.md`
