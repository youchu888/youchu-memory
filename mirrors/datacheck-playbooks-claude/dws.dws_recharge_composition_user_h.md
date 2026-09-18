# dws.dws_recharge_composition_user_h 核查剧本

## 1. 表信息
- 表名：`dws.dws_recharge_composition_user_h`
- 业务名：充值构成用户事实表
- 状态：上线
- 表说明：按 `dt + time_slot + app_id + channel + uid` 沉淀充值用户粒度事实，支撑充值构成分析、账龄分段、渠道充值 ROI 等场景
- 目标粒度：`dt + time_slot + app_id + channel + uid`
- 核心指标：`recharge_amount`、`recharge_order_count`、`recharge_user_flag`、`vip_recharge_amount`、`coin_recharge_amount`
- 关键维度：`register_time`、`register_date`、`user_type`、`user_type_source`

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`time_slot_start`、`time_slot_end`、`app_id`、`channel`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该日全量时间槽
  - 传 `dt + app_id`：核查指定 app
  - 传 `time_slot_start/time_slot_end`：仅核查指定时间槽范围
  - `channel` 仅用于下钻，不改变最终对账粒度

## 3. 绑定程序
- 绑定处理程序（DDL）：`ops_system/04.dws/dws_recharge_composition_user_h/dws_recharge_composition_user_h_ddl.sql`
- 绑定处理程序（小时）：`ops_system/04.dws/dws_recharge_composition_user_h/dws_recharge_composition_user_h_hourly.sql`
- 绑定处理程序（日终）：`ops_system/04.dws/dws_recharge_composition_user_h/dws_recharge_composition_user_h_daily.sql`
- 数据来源表：
  - `dwd.dwd_order_paid_d`：充值订单事实（主数据源）
  - `dim.dim_user_all`：用户维度（channel、register_time、user_type 补齐）
- 关键逻辑块：
  - `order_agg`：按 `dt + time_slot + app_id + uid` 聚合支付事实，只计 `currency = 'CNY'` 的金额
  - `dim.dim_user_all` LEFT JOIN：补齐 `channel`（COALESCE 为 'organic'）、`register_time`、`register_date`、`user_type`
  - `user_type_source`：固定写 `'dim_user_all'`
- 调度方式：
  - **小时任务**（`INSERT INTO`）：处理当前 slot 的 event_time 窗口，主键表 upsert
  - **日终任务**（`INSERT OVERWRITE PARTITION`）：按 `dt = '${dt}'` 全量重算 T-1 分区，原子替换
- channel 归一规则：`COALESCE(dim_user_all.channel, 'organic')`，用户级 canonical channel（first-non-organic-wins）
- 已确认逻辑：
  - 金额口径：仅 `currency = 'CNY'`
  - 订单类型拆分：`vip_subscription` → `vip_recharge_amount`；`coin_purchase` → `coin_recharge_amount`
  - `recharge_amount` = 全类型 CNY 订单金额（含 vip + coin + 其他）
  - `recharge_order_count` = `COUNT(DISTINCT order_id)`
  - `recharge_user_flag` = `CASE WHEN recharge_order_count > 0 THEN 1 ELSE 0 END`
  - `register_date` = `DATE(dim_user_all.register_time)`，老用户可能为 `2025-12-20`（兜底值）
- 程序维护约定：若来源表、连接键、金额口径、订单类型映射、channel 归一规则或 dim 关联逻辑变化，必须同步更新本剧本

## 4. 核查 parts

### part_01_basic_shape_and_uniqueness
- 目的：确认目标表基础形态、主键唯一性、关键空值与值域是否合法
- 来源表：`dws.dws_recharge_composition_user_h`
- 核查重点：
  - 指定日期是否有数据
  - 主键 `dt + time_slot + app_id + channel + uid` 是否唯一
  - `user_type` 是否仅出现 `vip / normal / NULL`（NULL 为 dim 未关联到的用户）
  - `recharge_user_flag` 是否仅出现 `0 / 1`
  - 金额、订单数是否出现负值
  - `recharge_user_flag = 0` 时是否仍有金额或订单数
- 判定：任一关键规则不满足，则该 part 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_id) AS app_cnt,
  COUNT(DISTINCT time_slot) AS slot_cnt,
  COUNT(DISTINCT CONCAT(app_id, '|', uid)) AS user_cnt,
  SUM(recharge_amount) AS total_recharge_amount,
  SUM(recharge_order_count) AS total_recharge_order_count,
  SUM(recharge_user_flag) AS total_recharge_user_count
FROM dws.dws_recharge_composition_user_h
WHERE dt = '{{dt}}'
  {{time_slot_filter}}
  {{app_filter}}
  {{channel_filter}};
```

#### SQL：主键重复检查
```sql
SELECT
  dt, time_slot, app_id, channel, uid,
  COUNT(*) AS dup_cnt
FROM dws.dws_recharge_composition_user_h
WHERE dt = '{{dt}}'
  {{time_slot_filter}}
  {{app_filter}}
  {{channel_filter}}
GROUP BY dt, time_slot, app_id, channel, uid
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：值域与负值检查
```sql
SELECT *
FROM dws.dws_recharge_composition_user_h
WHERE dt = '{{dt}}'
  {{time_slot_filter}}
  {{app_filter}}
  {{channel_filter}}
  AND (
    (user_type IS NOT NULL AND user_type NOT IN ('vip', 'normal'))
    OR recharge_user_flag NOT IN (0, 1)
    OR COALESCE(recharge_amount, 0) < 0
    OR COALESCE(recharge_order_count, 0) < 0
    OR COALESCE(vip_recharge_amount, 0) < 0
    OR COALESCE(coin_recharge_amount, 0) < 0
    OR (COALESCE(recharge_user_flag, 0) = 0 AND (COALESCE(recharge_amount, 0) <> 0 OR COALESCE(recharge_order_count, 0) <> 0))
  )
LIMIT 100;
```

### part_02_order_fact_reconciliation
- 目的：按支付来源表重算目标表核心充值指标并对账
- 来源表：`dwd.dwd_order_paid_d`
- 对齐粒度：`dt + app_id + uid`（跨 channel 汇总，因为 channel 来自 dim_user_all 不来自订单事件）
- 目标字段：`recharge_amount`、`recharge_order_count`、`vip_recharge_amount`、`coin_recharge_amount`
- 关键规则：
  - 仅统计 `currency = 'CNY'`
  - `recharge_order_count = COUNT(DISTINCT order_id)`
  - `vip_recharge_amount` 仅统计 `order_type = 'vip_subscription'`
  - `coin_recharge_amount` 仅统计 `order_type = 'coin_purchase'`
  - 注意：目标表的 channel 来自 dim_user_all，不来自 dwd_order_paid_d.channel；对账时按 `(app_id, uid)` 聚合忽略 channel 差异
- 判定：SUM 级金额不一致，则该 part 失败

#### SQL：来源重算与总量对比
```sql
SELECT
  'dwd' AS src,
  COUNT(DISTINCT CONCAT(app_id, '|', uid)) AS users,
  SUM(CASE WHEN currency = 'CNY' THEN amount ELSE 0 END) AS recharge_amount,
  SUM(CASE WHEN currency = 'CNY' AND order_type = 'vip_subscription' THEN amount ELSE 0 END) AS vip_amount,
  SUM(CASE WHEN currency = 'CNY' AND order_type = 'coin_purchase' THEN amount ELSE 0 END) AS coin_amount
FROM dwd.dwd_order_paid_d
WHERE dt = '{{dt}}'
  {{app_filter}}
UNION ALL
SELECT
  'dws',
  COUNT(DISTINCT CONCAT(app_id, '|', uid)),
  SUM(recharge_amount),
  SUM(vip_recharge_amount),
  SUM(coin_recharge_amount)
FROM dws.dws_recharge_composition_user_h
WHERE dt = '{{dt}}'
  {{app_filter}};
```

### part_03_dim_user_enrichment_reconciliation
- 目的：核对目标表中来自 `dim.dim_user_all` 的补齐字段是否正确
- 来源表：`dim.dim_user_all`
- 对齐粒度：`app_id + uid`
- 目标字段：`channel`、`register_time`、`register_date`、`user_type`
- 关键规则：
  - `channel = COALESCE(dim_user_all.channel, 'organic')`
  - `register_date = DATE(dim_user_all.register_time)`
  - `user_type = CASE WHEN dim_user_all.user_type = 'vip' THEN 'vip' ELSE 'normal' END`
  - `user_type_source` 固定为 `'dim_user_all'`
  - 注意：dim_user_all 是活表，hourly 持续更新。核查时 dim 快照与 ETL 运行时可能有微差（channel/user_type 变更），导致少量不一致属正常
- 判定：大面积不一致则失败；个位数差异由 dim 活表时差引起，可接受

#### SQL：channel 一致性检查
```sql
SELECT
  SUM(CASE WHEN d.channel = COALESCE(dua.channel, 'organic') THEN 1 ELSE 0 END) AS ch_match,
  SUM(CASE WHEN d.channel <> COALESCE(dua.channel, 'organic') THEN 1 ELSE 0 END) AS ch_mismatch,
  SUM(CASE WHEN dua.app_id IS NULL THEN 1 ELSE 0 END) AS dim_miss,
  COUNT(*) AS total
FROM dws.dws_recharge_composition_user_h d
LEFT JOIN dim.dim_user_all dua
  ON d.app_id = dua.app_id AND d.uid = dua.uid
WHERE d.dt = '{{dt}}'
  {{app_filter}};
```

### part_04_metric_consistency
- 目的：检查目标表内部指标关系是否自洽
- 核查重点：
  - `vip_recharge_amount + coin_recharge_amount <= recharge_amount`
  - `recharge_order_count = 0` 时 `recharge_amount` 必须为 0
  - `recharge_user_flag = 1` 时 `recharge_order_count` 必须大于 0
- 判定：任一规则不满足，则该 part 失败

#### SQL：内部一致性异常样本
```sql
SELECT *
FROM dws.dws_recharge_composition_user_h
WHERE dt = '{{dt}}'
  {{time_slot_filter}}
  {{app_filter}}
  {{channel_filter}}
  AND (
    COALESCE(vip_recharge_amount, 0) + COALESCE(coin_recharge_amount, 0) > COALESCE(recharge_amount, 0)
    OR (COALESCE(recharge_order_count, 0) = 0 AND COALESCE(recharge_amount, 0) <> 0)
    OR (COALESCE(recharge_user_flag, 0) = 1 AND COALESCE(recharge_order_count, 0) <= 0)
  )
LIMIT 100;
```

### part_05_query_layer_consistency
- 目的：检查账龄桶汇总与全量汇总是否一致
- 核查重点：
  - 按账龄桶汇总后，各桶充值金额之和 = 总充值金额
  - 注意：`register_date` 为 `2025-12-20`（兜底值）的老用户会全部落入 `register_30d_plus` 桶
- 判定：汇总关系不成立则失败

#### SQL：账龄桶汇总一致性
```sql
WITH base AS (
  SELECT
    dt, app_id, uid,
    recharge_amount,
    CASE
      WHEN register_date IS NULL THEN 'unknown'
      WHEN DATEDIFF(dt, register_date) = 0 THEN 'register_day'
      WHEN DATEDIFF(dt, register_date) BETWEEN 1 AND 3 THEN 'register_1_3d'
      WHEN DATEDIFF(dt, register_date) BETWEEN 4 AND 7 THEN 'register_4_7d'
      WHEN DATEDIFF(dt, register_date) BETWEEN 8 AND 15 THEN 'register_8_15d'
      WHEN DATEDIFF(dt, register_date) BETWEEN 16 AND 30 THEN 'register_16_30d'
      ELSE 'register_30d_plus'
    END AS reg_bucket
  FROM dws.dws_recharge_composition_user_h
  WHERE dt = '{{dt}}'
    {{app_filter}}
)
SELECT
  SUM(recharge_amount) AS bucket_sum,
  (SELECT SUM(recharge_amount) FROM dws.dws_recharge_composition_user_h WHERE dt = '{{dt}}' {{app_filter}}) AS total_sum,
  SUM(recharge_amount) - (SELECT SUM(recharge_amount) FROM dws.dws_recharge_composition_user_h WHERE dt = '{{dt}}' {{app_filter}}) AS diff
FROM base;
```

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_recharge_composition_user_h/`
- 报告需包含：
  1. 结论：明确是否通过"来源对账 + 维度补齐 + 内部一致性"
  2. 核查大类汇总：基础形态、支付来源对账、channel 一致性、内部指标一致性、账龄桶一致性
  3. 逐条规则结果：每条规则都要给出核验范围、异常量、结论
  4. 问题与处理建议：区分来源错误、dim 快照时差、查询层口径问题
- 报告中的所有结论都应带数据，不能只写口头判断

## 6. 剧本维护约定
- 若目标表主键、金额口径、订单类型口径、channel 归一规则、dim 关联来源或账龄桶规则变化，必须同步更新本剧本
- dim_user_all 是活表，核查 channel 一致性时允许个位数差异（dim hourly 更新导致的快照时差）
