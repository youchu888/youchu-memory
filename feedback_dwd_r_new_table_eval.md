---
name: feedback_dwd_r_new_table_eval
description: 新建 dwd_r 前必须评估量级/分桶；merge-engine 默认不保留第一条
type: feedback
---

# 新建 dwd_r：先评估再落 DDL

**以后怎么做**：任务涉及新建 `dwd_*_r`（含 fanout 写表）时，**先评估、跟业务确认、自估增量**，再写 DDL / 找斯科特合入。禁止拍脑袋定 bucket，也禁止默认开 `first-row`。

## 开工清单（缺一不可）

1. **跟业务确认**：事件名、主键粒度、是否要实时 `_r`、下游用途
2. **自估增量**：日量级、峰值、与现网同事件/同量级表对照（产线探数，禁 test 估产）
3. **定数据规模**：预估单日行数与文件体积量级
4. **定分桶数**：按产线量级 + 现网同类 fanout 表对照选 `bucket` / `sinkParallelism`；DDL、manifest、design 三处同数
5. **是否保留第一条**：`merge-engine=first-row` **默认不要**；只有业务明确要求「同 key 只留首条且后续不覆盖」才开（如订单全局去重）

## 保留第一条（first-row）默认否

| 场景 | 做法 |
|------|------|
| 一般事件明细 / 曝光点击等 | **不用** first-row；用默认 deduplicate 或业务指定引擎 |
| 同 key 必须只留首条、后写不可改 | 才开 `first-row`，并在 design/DDL 注释写明业务理由 |

**错了会怎样**：bucket 建表后改不了；误开 first-row → 晚到/重报无法更新，口径永久偏。

关联：
- 产线探 bucket：`feedback_prod_bucket_from_prod_probe.md`（红线 #33）
- 合入找斯科特：`feedback_dwd_r_ddl_direct_to_scott.md`（红线 #34）
- lesson：`lessons/2026-11-09-新建dwd_r须评估量级分桶默认不保留第一条.md`
