---
name: dim_user_all 待重建改造项
description: dim_user_all 后续需要重建表+回刷的遗留改造，包括累计字段幂等和去掉 DEFAULT 值
type: project
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
dim_user_all 当前可用但有两类问题，需要在下一轮重建时一次性解决。

## 要做的事

1. **累计字段（total_coin_buy_* / total_vip_buy_* / total_consume_*）幂等化**
   - 当前 daily 是 `history + T-1 当日增量`，重跑 daily 会 double count（非幂等）
   - 方案：加一个汇总时间字段（如 `last_accumulated_dt DATE`），daily 累加前检查 `last_accumulated_dt < ${dt}` 才累加，等值就跳过；或直接从 `dwd_order_paid_d` 全历史重算（代价高但幂等）
2. **去掉 `channel_updated_time` 和 `create_time` 的 `DEFAULT CURRENT_TIMESTAMP`**
   - 当前 DDL 两个字段都有 DEFAULT CURRENT_TIMESTAMP
   - StarRocks 主键表的 UPDATE 实质是 delete+insert，未显式 SET 的 DEFAULT 字段会被刷成当前时间；曾经因此把 1.51 亿 organic 用户的 channel_updated_time 全部污染成 2026-04-15
   - 去掉 DEFAULT，改由 ETL 显式写入 `CURRENT_TIMESTAMP()` 或 `NULL`
3. **重建表 + 从 2026-01-01 回刷数据**
   - StarRocks 不允许 ALTER 修改列的默认值；只能 drop + create + 回刷
   - 回刷起点 = 2026-01-01（覆盖全部有效 DWD 数据，DWD 数据自 2025-12-20 起）

## 目前可以用的变通方案（不推荐长期）

- daily 只跑一次/日，依赖调度层保证幂等
- migration Step 8 `UPDATE ... SET channel_updated_time = NULL WHERE channel = 'organic'` 清脏

**Why:** 这些改动不能增量做（StarRocks DDL 限制 + 累计字段语义变更），要一次性窗口做完；在做之前继续使用现有表。

**How to apply:** 用户主动提出做重建时，恢复这个上下文；检查当时 dim_user_all 的现状（是否有人手动修过 DDL、是否已经有累计字段问题暴露），按上面 3 步走。
