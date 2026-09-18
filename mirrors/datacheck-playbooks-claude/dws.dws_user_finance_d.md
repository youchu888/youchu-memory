# dws.dws_user_finance_d 用户日增量金额指标核查剧本

## 1. 表信息
- 目标表：`dws.dws_user_finance_d`
- 业务名：用户日增量金额指标（充值 + 金币消费 + 期初期末余额）
- 状态：重构后首次上线
- 表说明：每个 `(dt, app_id, uid)` 一行，承载该用户该日的**充值 delta + 消费 delta + 期初/期末金币余额**
- 目标粒度：`dt + app_id + uid`
- 分区：按 `dt` 日分区，幂等重跑只覆盖该分区
- 生成规则：
  - 当日有充值（`dwd_order_paid_d`）或消费（`dwd_coin_consume_h`）→ 生成一行
  - 两边都没有 → **不生成**
- 余额优先级：**有上报（dwd 的 balance_before/after）就用上报；没有就 prev_day_eod 兜底为 0**
- 余额口径：
  - `coin_balance_sod`：首笔消费前余额；无消费时 = `COALESCE(prev_day_eod, 0)`
  - `coin_balance_eod`：末次金币变动后余额；有消费 = 末笔 `balance_after` + 消费后 coin_purchase；无消费 + 有 coin_purchase = `COALESCE(prev_day_eod, 0) + 当日 coin_quantity`；无消费仅买 vip = `COALESCE(prev_day_eod, 0)`
- `prev_day_eod` 取数：历史上最近一日 `dws_user_finance_d` 中**非 NULL 的 eod**（不限定"有消费"，让 only-vip / only-coin_purchase 老用户也能继承；真首充用户历史无行 → 取 0）
- 守恒等式（仅对当日有消费的行）：`sod - 当日 consume + 末笔消费后的 coin_purchase = eod`

## 2. 参数约定
- 必填：`dt`（核查日期，一般 T-1）
- 选填：`app_code` / `app_id`、`uid`
- `dt` 语义：验证"该 dt 日分区内的数据"

## 3. 绑定程序
- DDL：`ops_system/04.dws/dws_user_finance_d/dws_user_finance_d_ddl.sql`
- 小时 ETL：`ops_system/04.dws/dws_user_finance_d/dws_user_finance_d_hourly.sql`（UPSERT）
- 日终 ETL：`ops_system/04.dws/dws_user_finance_d/dws_user_finance_d_daily.sql`（INSERT OVERWRITE PARTITION）
- 数据来源表：
  - `dwd.dwd_order_paid_d`：充值明细（`order_type = coin_purchase / vip_subscription`，字段：`amount`（分）/ `coin_quantity`（金币枚数））
  - `dwd.dwd_coin_consume_h`：金币消费明细（字段：`coin_consume_amount` / `coin_balance_before` / `coin_balance_after`）
- 关键逻辑块：
  - 充值聚合：按 app_id, uid 计总笔数/金额，按 order_type 拆出 coin_buy / vip_buy
  - 消费聚合：按 app_id, uid 计次数/金额，MIN_BY 拿首笔 balance_before，MAX_BY 拿末笔 balance_after 和 last_consume_event_time
  - 余额调整：`purchase_after_last_consume` = 末笔消费 event_time 之后的 coin_purchase.coin_quantity 之和
  - 无消费场景：从历史分区取 `prev_day_eod`（最近有 consume 记录日的 eod）
- 程序维护约定：若 order_type 枚举、coin_quantity 语义、consume 字段变化，必须同步更新本剧本

## 4. 核查 parts

### part_01_basic_shape_and_uniqueness
- 目的：基础形态、主键唯一、负值与空值检查
- 核查重点：
  - 分区 `dt = {{dt}}` 有数据
  - 主键 `(dt, app_id, uid)` 唯一
  - 所有 delta 字段非负（注意：`coin_consume_amount < 0` 是 dwd 上报问题，dws 透传，**不算 dws 失败但需告警**）
  - `recharge_count / recharge_amount` = `coin_buy_* + vip_buy_*` 恒等
  - 两边都为 0（即 `recharge_count = 0 AND coin_consume_count = 0`）的行不应存在
  - **`coin_balance_sod` / `coin_balance_eod` 不应为 NULL**（新逻辑后真首充也兜底为 0）
- 判定：任一关键规则不满足 → 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_id) AS app_cnt,
  COUNT(DISTINCT uid) AS uid_cnt,
  SUM(recharge_count) AS sum_recharge_count,
  SUM(recharge_amount) AS sum_recharge_amount,
  SUM(coin_buy_amount) + SUM(vip_buy_amount) AS sum_by_types,
  SUM(coin_consume_count) AS sum_consume_count,
  SUM(coin_consume_amount) AS sum_consume_amount,
  SUM(CASE WHEN coin_balance_sod IS NULL THEN 1 ELSE 0 END) AS null_sod,
  SUM(CASE WHEN coin_balance_eod IS NULL THEN 1 ELSE 0 END) AS null_eod
FROM dws.dws_user_finance_d
WHERE dt = '{{dt}}'
  {{app_filter}};
```

#### SQL：主键唯一性
```sql
SELECT dt, app_id, uid, COUNT(*) AS cnt
FROM dws.dws_user_finance_d
WHERE dt = '{{dt}}'
  {{app_filter}}
GROUP BY dt, app_id, uid
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：负值 / 空行 / recharge 恒等
```sql
SELECT *
FROM dws.dws_user_finance_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    recharge_count < 0 OR recharge_amount < 0
    OR coin_buy_count < 0 OR coin_buy_amount < 0
    OR vip_buy_count < 0 OR vip_buy_amount < 0
    OR coin_consume_count < 0 OR coin_consume_amount < 0
    OR (recharge_count = 0 AND coin_consume_count = 0)
    OR recharge_count <> (coin_buy_count + vip_buy_count)
    OR recharge_amount <> (coin_buy_amount + vip_buy_amount)
  )
LIMIT 100;
```

### part_02_delta_source_reconciliation
- 目的：`recharge_*` / `coin_buy_*` / `vip_buy_*` / `coin_consume_*` 与 dwd 源对账
- 最终对齐粒度：`dt + app_id + uid`
- 判定：任一字段有差异的行 = 0

#### SQL：充值侧对账（按 uid 粒度）
```sql
WITH src AS (
  SELECT app_id, uid,
    SUM(CASE WHEN order_type IN ('coin_purchase','vip_subscription') THEN 1 ELSE 0 END)      AS src_recharge_count,
    SUM(CASE WHEN order_type IN ('coin_purchase','vip_subscription') THEN amount ELSE 0 END) AS src_recharge_amount,
    SUM(CASE WHEN order_type = 'coin_purchase'    THEN 1 ELSE 0 END)      AS src_coin_buy_count,
    SUM(CASE WHEN order_type = 'coin_purchase'    THEN amount ELSE 0 END) AS src_coin_buy_amount,
    SUM(CASE WHEN order_type = 'vip_subscription' THEN 1 ELSE 0 END)      AS src_vip_buy_count,
    SUM(CASE WHEN order_type = 'vip_subscription' THEN amount ELSE 0 END) AS src_vip_buy_amount
  FROM dwd.dwd_order_paid_d
  WHERE dt = '{{dt}}' AND app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid,
       t.recharge_count, src.src_recharge_count,
       t.recharge_amount, src.src_recharge_amount,
       t.coin_buy_count, src.src_coin_buy_count,
       t.coin_buy_amount, src.src_coin_buy_amount,
       t.vip_buy_count, src.src_vip_buy_count,
       t.vip_buy_amount, src.src_vip_buy_amount
FROM dws.dws_user_finance_d t
FULL OUTER JOIN src ON t.app_id = src.app_id AND t.uid = src.uid
WHERE t.dt = '{{dt}}'
  AND (
    COALESCE(t.recharge_count, 0)  <> COALESCE(src.src_recharge_count, 0)
    OR COALESCE(t.recharge_amount, 0) <> COALESCE(src.src_recharge_amount, 0)
    OR COALESCE(t.coin_buy_count, 0) <> COALESCE(src.src_coin_buy_count, 0)
    OR COALESCE(t.coin_buy_amount, 0) <> COALESCE(src.src_coin_buy_amount, 0)
    OR COALESCE(t.vip_buy_count, 0) <> COALESCE(src.src_vip_buy_count, 0)
    OR COALESCE(t.vip_buy_amount, 0) <> COALESCE(src.src_vip_buy_amount, 0)
  )
LIMIT 100;
```

#### SQL：消费侧对账（按 uid 粒度）
```sql
WITH src AS (
  SELECT app_id, uid,
    COUNT(event_id) AS src_coin_consume_count,
    SUM(COALESCE(coin_consume_amount, 0)) AS src_coin_consume_amount
  FROM dwd.dwd_coin_consume_h
  WHERE dt = '{{dt}}' AND app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid,
       t.coin_consume_count, src.src_coin_consume_count,
       t.coin_consume_amount, src.src_coin_consume_amount
FROM dws.dws_user_finance_d t
FULL OUTER JOIN src ON t.app_id = src.app_id AND t.uid = src.uid
WHERE t.dt = '{{dt}}'
  AND (
    COALESCE(t.coin_consume_count, 0)  <> COALESCE(src.src_coin_consume_count, 0)
    OR COALESCE(t.coin_consume_amount, 0) <> COALESCE(src.src_coin_consume_amount, 0)
  )
LIMIT 100;
```

#### SQL：按 dt 合计对账（单指标全量）
```sql
SELECT
  'target' AS src,
  SUM(recharge_count) AS rec_cnt, SUM(recharge_amount) AS rec_amt,
  SUM(coin_buy_count) AS cb_cnt,  SUM(coin_buy_amount) AS cb_amt,
  SUM(vip_buy_count) AS vb_cnt,   SUM(vip_buy_amount) AS vb_amt,
  SUM(coin_consume_count) AS cc_cnt, SUM(coin_consume_amount) AS cc_amt
FROM dws.dws_user_finance_d WHERE dt = '{{dt}}' {{app_filter}}
UNION ALL
SELECT 'source_order',
  SUM(CASE WHEN order_type IN ('coin_purchase','vip_subscription') THEN 1 ELSE 0 END),
  SUM(CASE WHEN order_type IN ('coin_purchase','vip_subscription') THEN amount ELSE 0 END),
  SUM(CASE WHEN order_type = 'coin_purchase' THEN 1 ELSE 0 END),
  SUM(CASE WHEN order_type = 'coin_purchase' THEN amount ELSE 0 END),
  SUM(CASE WHEN order_type = 'vip_subscription' THEN 1 ELSE 0 END),
  SUM(CASE WHEN order_type = 'vip_subscription' THEN amount ELSE 0 END),
  NULL, NULL
FROM dwd.dwd_order_paid_d WHERE dt = '{{dt}}' {{app_filter}}
UNION ALL
SELECT 'source_consume',
  NULL, NULL, NULL, NULL, NULL, NULL,
  COUNT(event_id), SUM(COALESCE(coin_consume_amount, 0))
FROM dwd.dwd_coin_consume_h WHERE dt = '{{dt}}' {{app_filter}};
```

### part_03_balance_conservation
- 目的：验证余额守恒
- 适用范围：**仅对当日 `coin_consume_count > 0` 的行做严格守恒**（这些行 sod/eod 都来自 dwd 上报）
- 无消费的行 sod/eod 来自 prev_eod 继承（含真首充的 0 兜底），不做严格守恒，只做趋势监控
- 守恒等式（有消费场景）：`sod - coin_consume_amount + 末笔消费后的 coin_purchase.coin_quantity = eod`
- 无消费场景：`eod - COALESCE(prev_day_eod, 0) = 当日 coin_quantity 之和`（仅当有 coin_purchase 时）
- 判定：违反守恒的行数 / 样本占比需归因到 dwd（`balance_before - amount = balance_after` 的内在不一致率）；扣除 dwd 漂移后，dws 自身放大率应 < 1%

#### SQL：有消费场景守恒
```sql
WITH purchase_after AS (
  SELECT op.app_id, op.uid, SUM(op.coin_quantity) AS coins_after_last_consume
  FROM dwd.dwd_order_paid_d op
  INNER JOIN (
    SELECT app_id, uid, MAX(event_time) AS last_consume_time
    FROM dwd.dwd_coin_consume_h
    WHERE dt = '{{dt}}' AND app_id IS NOT NULL AND uid IS NOT NULL
      {{app_filter}}
    GROUP BY app_id, uid
  ) cc ON op.app_id = cc.app_id AND op.uid = cc.uid
  WHERE op.dt = '{{dt}}' AND op.order_type = 'coin_purchase'
    AND op.event_time > cc.last_consume_time
    {{app_filter}}
  GROUP BY op.app_id, op.uid
)
SELECT t.app_id, t.uid,
       t.coin_balance_sod, t.coin_consume_amount, t.coin_balance_eod,
       COALESCE(pa.coins_after_last_consume, 0) AS coins_after_last_consume,
       (t.coin_balance_sod - t.coin_consume_amount + COALESCE(pa.coins_after_last_consume, 0)) AS expected_eod,
       (t.coin_balance_eod - (t.coin_balance_sod - t.coin_consume_amount + COALESCE(pa.coins_after_last_consume, 0))) AS diff
FROM dws.dws_user_finance_d t
LEFT JOIN purchase_after pa ON t.app_id = pa.app_id AND t.uid = pa.uid
WHERE t.dt = '{{dt}}'
  AND t.coin_consume_count > 0
  AND t.coin_balance_sod IS NOT NULL AND t.coin_balance_eod IS NOT NULL
  AND t.coin_balance_eod <> (t.coin_balance_sod - t.coin_consume_amount + COALESCE(pa.coins_after_last_consume, 0))
  {{app_filter}}
LIMIT 100;
```

#### SQL：无消费场景守恒（仅 only_recharge 且买了 coin）
```sql
WITH purchase AS (
  SELECT app_id, uid, SUM(coin_quantity) AS src_purchase_coins
  FROM dwd.dwd_order_paid_d
  WHERE dt = '{{dt}}' AND order_type = 'coin_purchase'
    AND app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid, t.coin_balance_sod, t.coin_balance_eod, p.src_purchase_coins,
       (t.coin_balance_eod - COALESCE(t.coin_balance_sod, 0)) AS tgt_diff,
       p.src_purchase_coins AS expected_diff
FROM dws.dws_user_finance_d t
INNER JOIN purchase p ON t.app_id = p.app_id AND t.uid = p.uid
WHERE t.dt = '{{dt}}' AND t.coin_consume_count = 0
  AND t.coin_balance_eod IS NOT NULL
  AND (t.coin_balance_eod - COALESCE(t.coin_balance_sod, 0)) <> p.src_purchase_coins
  {{app_filter}}
LIMIT 100;
```

### part_04_generation_rule_coverage
- 目的：验证"两边都没有不生成"和"只有充值 or 只有消费也生成"的规则
- 判定：目标表行数应 = `{dwd_order_paid.uid} ∪ {dwd_coin_consume.uid}`

#### SQL：应生成但未生成的 uid
```sql
WITH active_users AS (
  SELECT DISTINCT app_id, uid FROM (
    SELECT app_id, uid FROM dwd.dwd_order_paid_d
    WHERE dt = '{{dt}}' AND app_id IS NOT NULL AND uid IS NOT NULL {{app_filter}}
    UNION ALL
    SELECT app_id, uid FROM dwd.dwd_coin_consume_h
    WHERE dt = '{{dt}}' AND app_id IS NOT NULL AND uid IS NOT NULL {{app_filter}}
  ) t
)
SELECT au.app_id, au.uid
FROM active_users au
LEFT JOIN dws.dws_user_finance_d t
  ON t.dt = '{{dt}}' AND t.app_id = au.app_id AND t.uid = au.uid
WHERE t.uid IS NULL
LIMIT 100;
```

#### SQL：不应生成但生成了的 uid
```sql
SELECT t.app_id, t.uid
FROM dws.dws_user_finance_d t
LEFT JOIN (
  SELECT app_id, uid FROM dwd.dwd_order_paid_d WHERE dt = '{{dt}}' {{app_filter}}
  UNION ALL SELECT app_id, uid FROM dwd.dwd_coin_consume_h WHERE dt = '{{dt}}' {{app_filter}}
) src ON t.app_id = src.app_id AND t.uid = src.uid
WHERE t.dt = '{{dt}}' AND src.uid IS NULL
  {{app_filter}}
LIMIT 100;
```

### part_05_partition_idempotency
- 目的：验证幂等重跑不污染其他分区
- 做法：对比重跑前后同 `{{dt}}` 分区的行数和指标 SUM；其他分区的数据不应变化
- 判定：其他分区指标 SUM 变化 = 0

#### SQL：分区行数分布（运维）
```sql
SELECT dt, COUNT(*) AS rows_per_day,
       SUM(recharge_amount) AS sum_recharge,
       SUM(coin_consume_amount) AS sum_consume
FROM dws.dws_user_finance_d
  {{app_filter}}
WHERE dt BETWEEN DATE_SUB(CAST('{{dt}}' AS DATE), INTERVAL 7 DAY) AND CAST('{{dt}}' AS DATE)
GROUP BY dt ORDER BY dt;
```

### part_06_exception_sampling_and_reporting
- 目的：统一输出异常样本
- 必含内容：
  - 主键冲突样本
  - delta 字段对账差异样本（order 侧 + consume 侧）
  - 守恒等式违反样本
  - 应生成未生成 / 不应生成却生成 的样本
  - `null_sod / null_eod` 数量（首次部署可能较高，标记风险）
- 判定：说明性输出

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_user_finance_d/`
- 文件名：`validate__{{dt}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：整体是否通过、失败 part 名称
  2. 核查大类汇总：基础形态、delta 对账、余额守恒、生成规则、分区幂等
  3. 逐条规则：核验范围（行数 / app 数）、异常量 / 样本量、数值 delta 与占比、结论
  4. 问题与处理建议：区分"程序 bug"、"源数据层漂移"、"金币来源/去向超出 dwd 覆盖"（守恒差异极少数可能源于业务层赠送/任务奖励）
  5. 所有结论带数据

## 6. 剧本维护约定
- 若 `order_type` 枚举、`coin_quantity` 语义、`coin_consume_h.balance_before/after` 字段变化，必须同步更新本剧本
- 若未来加入小时级分区表 `dws_user_finance_h` 或周/月表，新增对应 part
- 若引入非 `dwd_coin_consume_h` 的金币变动源（任务/奖励/退款），余额守恒等式需扩展并同步本剧本
