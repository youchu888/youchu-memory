# ads.ads_product_day_stat_d 核查剧本

## 1. 表信息
- 表名：`ads.ads_product_day_stat_d`
- 业务名：项目日报
- 状态：上线
- 表说明：APP 每日核心指标宽表

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_id` / `app_code`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该日期下全量 app
  - 传 `dt + app_id/app_code`：核查指定 app

## 3. 绑定程序
- 绑定处理程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/05.ads/job_ads_product_day_stat_d/ads_product_day_stat_d.sql`
- 当前绑定说明：来源核查默认以该 SQL 的已上线实现为程序参考，不需要在 `/datacheck` 时额外打开程序。
- 关键逻辑块：
  - `target_dates`：当次运行写入/回填 `T / T-1 / T-3 / T-7`
  - `dau_reg`：日活、注册、自然/渠道注册（来源 `ads.ads_app_metrics_daily_d` 的 bitmap）
  - `retention`：留存指标
  - `channel_promo`：下载页访问/点击
  - `new_user_reg` / `nat_new_user` / `chl_new_user`：按 `(dt, app_id, uid)` 识别当日新用户；**`nat`/`chl` 拆分按 `dim.dim_user_all.register_channel` 归一**（fallback 到 `dwd.channel`），避免同 uid 跨 channel 重复
  - `order_created` / `order_created_agg`：发起充值相关指标
  - `order_paid` / `order_paid_agg`：支付相关指标
  - `effective_active`：当日 `dwd.dwd_app_page_view_d` 中**单 uid ≥ 2 个不同 page_key** 的 uid 集合（per `dt, app_id`）
  - `effective_metrics`：5 个 effective 类指标按 `(dt, app_id)` 聚合（`effective_dau` / `effective_new_reg` / `effective_old_dau` / `effective_chl_new_reg` / `effective_nat_new_reg`）
  - `base_app`：最终 app 粒度汇总集合（含 effective_metrics）
- 程序维护约定：若 SQL 中的来源表、连接键、过滤条件、聚合逻辑或字段映射发生变化，必须同步更新本剧本与 `.claude/database/knowledge.md`。

## 4. 核查 parts

### part_01_total_vs_subtotal
- 目的：核查总字段与拆分字段之和是否一致
- 关注关系：
  - `dau_count = old_dau_count + new_dau_count`
  - `new_reg_count = new_reg_channel_count + new_reg_nature_count`
  - `order_created_users = new_order_created_users + old_order_created_users`
  - `order_created_cnt = new_order_created_cnt + old_order_created_cnt`
  - `order_created_amt = new_order_created_amt + old_order_created_amt`
  - `new_order_created_users = nat_new_order_created_users + chl_new_order_created_users`
  - `new_order_created_cnt = nat_new_order_created_cnt + chl_new_order_created_cnt`
  - `new_order_created_amt = nat_new_order_created_amt + chl_new_order_created_amt`
  - `order_pay_users = new_order_pay_users + old_order_pay_users`
  - `order_pay_cnt = new_order_pay_cnt + old_order_pay_cnt`
  - `order_pay_amt = new_order_pay_amt + old_order_pay_amt`
  - `new_order_pay_users = nat_new_order_pay_users + chl_new_order_pay_users`
  - `new_order_pay_cnt = nat_new_order_pay_cnt + chl_new_order_pay_cnt`
  - `new_order_pay_amt = nat_new_order_pay_amt + chl_new_order_pay_amt`
  - `effective_dau_count = effective_old_dau_count + effective_new_reg_count`
  - `effective_new_reg_count = effective_chl_new_reg_count + effective_nat_new_reg_count`
- 输出：
  1. 每个检查项的不一致行数
  2. 异常明细样本
- 判定：任一检查项不一致行数 > 0，则该 part 失败

#### SQL：前 10 条抽样
```sql
SELECT *
FROM ads.ads_product_day_stat_d
WHERE dt = '{{dt}}'
  {{app_filter}}
LIMIT 10;
```

#### SQL：总分核查汇总
```sql
SELECT
  COUNT(*) AS total_rows,
  SUM(CASE WHEN COALESCE(dau_count,0) = COALESCE(old_dau_count,0) + COALESCE(new_dau_count,0) THEN 0 ELSE 1 END) AS dau_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_reg_count,0) = COALESCE(new_reg_channel_count,0) + COALESCE(new_reg_nature_count,0) THEN 0 ELSE 1 END) AS new_reg_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_created_users,0) = COALESCE(new_order_created_users,0) + COALESCE(old_order_created_users,0) THEN 0 ELSE 1 END) AS created_users_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_created_cnt,0) = COALESCE(new_order_created_cnt,0) + COALESCE(old_order_created_cnt,0) THEN 0 ELSE 1 END) AS created_cnt_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_created_amt,0) = COALESCE(new_order_created_amt,0) + COALESCE(old_order_created_amt,0) THEN 0 ELSE 1 END) AS created_amt_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_created_users,0) = COALESCE(nat_new_order_created_users,0) + COALESCE(chl_new_order_created_users,0) THEN 0 ELSE 1 END) AS new_created_users_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_created_cnt,0) = COALESCE(nat_new_order_created_cnt,0) + COALESCE(chl_new_order_created_cnt,0) THEN 0 ELSE 1 END) AS new_created_cnt_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_created_amt,0) = COALESCE(nat_new_order_created_amt,0) + COALESCE(chl_new_order_created_amt,0) THEN 0 ELSE 1 END) AS new_created_amt_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_pay_users,0) = COALESCE(new_order_pay_users,0) + COALESCE(old_order_pay_users,0) THEN 0 ELSE 1 END) AS pay_users_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_pay_cnt,0) = COALESCE(new_order_pay_cnt,0) + COALESCE(old_order_pay_cnt,0) THEN 0 ELSE 1 END) AS pay_cnt_mismatch_rows,
  SUM(CASE WHEN COALESCE(order_pay_amt,0) = COALESCE(new_order_pay_amt,0) + COALESCE(old_order_pay_amt,0) THEN 0 ELSE 1 END) AS pay_amt_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_pay_users,0) = COALESCE(nat_new_order_pay_users,0) + COALESCE(chl_new_order_pay_users,0) THEN 0 ELSE 1 END) AS new_pay_users_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_pay_cnt,0) = COALESCE(nat_new_order_pay_cnt,0) + COALESCE(chl_new_order_pay_cnt,0) THEN 0 ELSE 1 END) AS new_pay_cnt_mismatch_rows,
  SUM(CASE WHEN COALESCE(new_order_pay_amt,0) = COALESCE(nat_new_order_pay_amt,0) + COALESCE(chl_new_order_pay_amt,0) THEN 0 ELSE 1 END) AS new_pay_amt_mismatch_rows
FROM ads.ads_product_day_stat_d
WHERE dt = '{{dt}}'
  {{app_filter}};
```

#### SQL：总分异常明细
```sql
SELECT *
FROM ads.ads_product_day_stat_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(dau_count,0) <> COALESCE(old_dau_count,0) + COALESCE(new_dau_count,0)
    OR COALESCE(new_reg_count,0) <> COALESCE(new_reg_channel_count,0) + COALESCE(new_reg_nature_count,0)
    OR COALESCE(order_created_users,0) <> COALESCE(new_order_created_users,0) + COALESCE(old_order_created_users,0)
    OR COALESCE(order_created_cnt,0) <> COALESCE(new_order_created_cnt,0) + COALESCE(old_order_created_cnt,0)
    OR COALESCE(order_created_amt,0) <> COALESCE(new_order_created_amt,0) + COALESCE(old_order_created_amt,0)
    OR COALESCE(new_order_created_users,0) <> COALESCE(nat_new_order_created_users,0) + COALESCE(chl_new_order_created_users,0)
    OR COALESCE(new_order_created_cnt,0) <> COALESCE(nat_new_order_created_cnt,0) + COALESCE(chl_new_order_created_cnt,0)
    OR COALESCE(new_order_created_amt,0) <> COALESCE(nat_new_order_created_amt,0) + COALESCE(chl_new_order_created_amt,0)
    OR COALESCE(order_pay_users,0) <> COALESCE(new_order_pay_users,0) + COALESCE(old_order_pay_users,0)
    OR COALESCE(order_pay_cnt,0) <> COALESCE(new_order_pay_cnt,0) + COALESCE(old_order_pay_cnt,0)
    OR COALESCE(order_pay_amt,0) <> COALESCE(new_order_pay_amt,0) + COALESCE(old_order_pay_amt,0)
    OR COALESCE(new_order_pay_users,0) <> COALESCE(nat_new_order_pay_users,0) + COALESCE(chl_new_order_pay_users,0)
    OR COALESCE(new_order_pay_cnt,0) <> COALESCE(nat_new_order_pay_cnt,0) + COALESCE(chl_new_order_pay_cnt,0)
    OR COALESCE(new_order_pay_amt,0) <> COALESCE(nat_new_order_pay_amt,0) + COALESCE(chl_new_order_pay_amt,0)
  )
LIMIT 100;
```

### part_02_detail_reconciliation
- 目的：按已绑定处理程序与来源表，对项目日报核心指标做来源重算与明细对账
- 程序绑定：`/Users/arthur/Program/datacenter/dc-parent/ops_system/05.ads/job_ads_product_day_stat_d/ads_product_day_stat_d.sql`
- 默认对齐粒度：`dt + app_id`
- 默认判定：目标表字段与来源重算结果逐项一致则通过，否则失败

#### part_02_01_dau_and_register_bitmap_reconciliation
- 对应程序逻辑块：`dau_reg`
- 来源表：`ads.ads_app_metrics_daily_d`
- 目标字段：`dau_count`、`old_dau_count`、`new_dau_count`、`new_reg_count`、`new_reg_channel_count`、`new_reg_nature_count`
- 已确认口径：
  - `new_dau_count = new_reg_count = bitmap_count(new_reg_ids)`
  - `old_dau_count = bitmap_count(bitmap_andnot(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty())))`
  - `dau_count = bitmap_count(bitmap_or(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty())))`
  - `new_reg_channel_count = bitmap_count(new_reg_channel_ids)`
  - `new_reg_nature_count = bitmap_count(new_reg_nature_ids)`
- 关键规则：所有 bitmap 运算都必须使用 `ifnull(..., bitmap_empty())` 做空值兜底。

##### SQL：来源重算
```sql
SELECT
  dt,
  app_id,
  bitmap_count(bitmap_or(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty()))) AS src_dau_count,
  bitmap_count(bitmap_andnot(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty()))) AS src_old_dau_count,
  bitmap_count(ifnull(new_reg_ids, bitmap_empty())) AS src_new_dau_count,
  bitmap_count(ifnull(new_reg_ids, bitmap_empty())) AS src_new_reg_count,
  bitmap_count(ifnull(new_reg_channel_ids, bitmap_empty())) AS src_new_reg_channel_count,
  bitmap_count(ifnull(new_reg_nature_ids, bitmap_empty())) AS src_new_reg_nature_count
FROM ads.ads_app_metrics_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
GROUP BY dt, app_id;
```

##### SQL：来源对账
```sql
WITH src AS (
  SELECT
    dt,
    app_id,
    bitmap_count(bitmap_or(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty()))) AS src_dau_count,
    bitmap_count(bitmap_andnot(ifnull(dau_ids, bitmap_empty()), ifnull(new_reg_ids, bitmap_empty()))) AS src_old_dau_count,
    bitmap_count(ifnull(new_reg_ids, bitmap_empty())) AS src_new_dau_count,
    bitmap_count(ifnull(new_reg_ids, bitmap_empty())) AS src_new_reg_count,
    bitmap_count(ifnull(new_reg_channel_ids, bitmap_empty())) AS src_new_reg_channel_count,
    bitmap_count(ifnull(new_reg_nature_ids, bitmap_empty())) AS src_new_reg_nature_count
  FROM ads.ads_app_metrics_daily_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
  GROUP BY dt, app_id
)
SELECT
  t.dt,
  t.app_id,
  t.dau_count,
  src.src_dau_count,
  t.old_dau_count,
  src.src_old_dau_count,
  t.new_dau_count,
  src.src_new_dau_count,
  t.new_reg_count,
  src.src_new_reg_count,
  t.new_reg_channel_count,
  src.src_new_reg_channel_count,
  t.new_reg_nature_count,
  src.src_new_reg_nature_count
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(t.dau_count, 0) <> COALESCE(src.src_dau_count, 0)
    OR COALESCE(t.old_dau_count, 0) <> COALESCE(src.src_old_dau_count, 0)
    OR COALESCE(t.new_dau_count, 0) <> COALESCE(src.src_new_dau_count, 0)
    OR COALESCE(t.new_reg_count, 0) <> COALESCE(src.src_new_reg_count, 0)
    OR COALESCE(t.new_reg_channel_count, 0) <> COALESCE(src.src_new_reg_channel_count, 0)
    OR COALESCE(t.new_reg_nature_count, 0) <> COALESCE(src.src_new_reg_nature_count, 0)
  )
LIMIT 100;
```

#### part_02_02_created_order_recalculation
- 对应程序逻辑块：`new_user_reg`、`nat_new_user`、`chl_new_user`、`order_created`、`order_created_agg`
- 来源表：`dwd.dwd_order_created_h`、`dwd.dwd_user_register_d_v2`
- 目标字段：所有 `*created*` 指标
- 已确认口径：
  - `order_created_users/cnt/amt` 通过 `dwd.dwd_order_created_h` 直接重算
  - `new_order_created_*` 通过当日注册用户集合 `new_user_reg` 按 `(dt, uid, app_id)` 关联识别
  - `nat_new_order_created_*` / `chl_new_order_created_*` 分别通过 `nat_new_user` / `chl_new_user` 按 `(dt, uid, app_id)` 关联识别
  - `old_order_created_* = order_created_* - new_order_created_*`
- 过滤条件：`order_type IN ('coin_purchase', 'vip_subscription')` 且 `currency = 'CNY'`
- 关键规则：充值相关的新老/自然/渠道划分均以注册表口径为准，不再按 channel 直接关联订单。

##### SQL：来源对账
```sql
WITH new_user_reg AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
),
nat_new_user AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    AND channel = 'organic'
),
chl_new_user AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    AND channel != 'organic'
),
src AS (
  SELECT
    r.dt,
    r.app_id,
    BITMAP_UNION_COUNT(TO_BITMAP(bitmap_hash64_udf(r.uid))) AS src_order_created_users,
    BITMAP_UNION_COUNT(TO_BITMAP(bitmap_hash64_udf(r.event_id))) AS src_order_created_cnt,
    SUM(r.amount) AS src_order_created_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN n.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_new_order_created_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN n.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_new_order_created_cnt,
    SUM(CASE WHEN n.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_new_order_created_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN nat.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_nat_new_order_created_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN nat.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_nat_new_order_created_cnt,
    SUM(CASE WHEN nat.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_nat_new_order_created_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN chl.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_chl_new_order_created_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN chl.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_chl_new_order_created_cnt,
    SUM(CASE WHEN chl.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_chl_new_order_created_amt
  FROM dwd.dwd_order_created_h r
  LEFT JOIN new_user_reg n
    ON r.dt = n.dt AND r.uid = n.uid AND r.app_id = n.app_id
  LEFT JOIN nat_new_user nat
    ON r.dt = nat.dt AND r.uid = nat.uid AND r.app_id = nat.app_id
  LEFT JOIN chl_new_user chl
    ON r.dt = chl.dt AND r.uid = chl.uid AND r.app_id = chl.app_id
  WHERE r.dt = '{{dt}}'
    {{app_filter}}
    AND r.order_type IN ('coin_purchase', 'vip_subscription')
    AND r.currency = 'CNY'
  GROUP BY r.dt, r.app_id
)
SELECT
  t.dt,
  t.app_id,
  t.order_created_users,
  src.src_order_created_users,
  t.order_created_cnt,
  src.src_order_created_cnt,
  t.order_created_amt,
  src.src_order_created_amt,
  t.new_order_created_users,
  src.src_new_order_created_users,
  t.new_order_created_cnt,
  src.src_new_order_created_cnt,
  t.new_order_created_amt,
  src.src_new_order_created_amt,
  t.old_order_created_users,
  src.src_order_created_users - src.src_new_order_created_users AS src_old_order_created_users,
  t.old_order_created_cnt,
  src.src_order_created_cnt - src.src_new_order_created_cnt AS src_old_order_created_cnt,
  t.old_order_created_amt,
  src.src_order_created_amt - src.src_new_order_created_amt AS src_old_order_created_amt,
  t.nat_new_order_created_users,
  src.src_nat_new_order_created_users,
  t.nat_new_order_created_cnt,
  src.src_nat_new_order_created_cnt,
  t.nat_new_order_created_amt,
  src.src_nat_new_order_created_amt,
  t.chl_new_order_created_users,
  src.src_chl_new_order_created_users,
  t.chl_new_order_created_cnt,
  src.src_chl_new_order_created_cnt,
  t.chl_new_order_created_amt,
  src.src_chl_new_order_created_amt
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(t.order_created_users, 0) <> COALESCE(src.src_order_created_users, 0)
    OR COALESCE(t.order_created_cnt, 0) <> COALESCE(src.src_order_created_cnt, 0)
    OR COALESCE(t.order_created_amt, 0) <> COALESCE(src.src_order_created_amt, 0)
    OR COALESCE(t.new_order_created_users, 0) <> COALESCE(src.src_new_order_created_users, 0)
    OR COALESCE(t.new_order_created_cnt, 0) <> COALESCE(src.src_new_order_created_cnt, 0)
    OR COALESCE(t.new_order_created_amt, 0) <> COALESCE(src.src_new_order_created_amt, 0)
    OR COALESCE(t.old_order_created_users, 0) <> COALESCE(src.src_order_created_users - src.src_new_order_created_users, 0)
    OR COALESCE(t.old_order_created_cnt, 0) <> COALESCE(src.src_order_created_cnt - src.src_new_order_created_cnt, 0)
    OR COALESCE(t.old_order_created_amt, 0) <> COALESCE(src.src_order_created_amt - src.src_new_order_created_amt, 0)
    OR COALESCE(t.nat_new_order_created_users, 0) <> COALESCE(src.src_nat_new_order_created_users, 0)
    OR COALESCE(t.nat_new_order_created_cnt, 0) <> COALESCE(src.src_nat_new_order_created_cnt, 0)
    OR COALESCE(t.nat_new_order_created_amt, 0) <> COALESCE(src.src_nat_new_order_created_amt, 0)
    OR COALESCE(t.chl_new_order_created_users, 0) <> COALESCE(src.src_chl_new_order_created_users, 0)
    OR COALESCE(t.chl_new_order_created_cnt, 0) <> COALESCE(src.src_chl_new_order_created_cnt, 0)
    OR COALESCE(t.chl_new_order_created_amt, 0) <> COALESCE(src.src_chl_new_order_created_amt, 0)
  )
LIMIT 100;
```

#### part_02_03_paid_order_recalculation
- 对应程序逻辑块：`new_user_reg`、`nat_new_user`、`chl_new_user`、`order_paid`、`order_paid_agg`
- 来源表：`dwd.dwd_order_paid_d`、`dwd.dwd_user_register_d_v2`
- 目标字段：所有 `*pay*` 指标
- 已确认口径：
  - `order_pay_users/cnt/amt` 通过 `dwd.dwd_order_paid_d` 直接重算
  - `new_order_pay_*` 通过当日注册用户集合 `new_user_reg` 按 `(dt, uid, app_id)` 关联识别
  - `nat_new_order_pay_*` / `chl_new_order_pay_*` 分别通过 `nat_new_user` / `chl_new_user` 按 `(dt, uid, app_id)` 关联识别
  - `old_order_pay_* = order_pay_* - new_order_pay_*`
- 过滤条件：`order_type IN ('coin_purchase', 'vip_subscription')` 且 `currency = 'CNY'`
- 关键规则：支付类指标与发起充值类指标口径平行，均以支付/发起事件事实表重新结算。

##### SQL：来源对账
```sql
WITH new_user_reg AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
),
nat_new_user AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    AND channel = 'organic'
),
chl_new_user AS (
  SELECT DISTINCT dt, uid, app_id
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    AND channel != 'organic'
),
src AS (
  SELECT
    r.dt,
    r.app_id,
    BITMAP_UNION_COUNT(TO_BITMAP(bitmap_hash64_udf(r.uid))) AS src_order_pay_users,
    BITMAP_UNION_COUNT(TO_BITMAP(bitmap_hash64_udf(r.event_id))) AS src_order_pay_cnt,
    SUM(r.amount) AS src_order_pay_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN n.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_new_order_pay_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN n.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_new_order_pay_cnt,
    SUM(CASE WHEN n.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_new_order_pay_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN nat.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_nat_new_order_pay_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN nat.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_nat_new_order_pay_cnt,
    SUM(CASE WHEN nat.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_nat_new_order_pay_amt,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN chl.uid IS NOT NULL THEN bitmap_hash64_udf(r.uid) END)) AS src_chl_new_order_pay_users,
    BITMAP_UNION_COUNT(TO_BITMAP(CASE WHEN chl.uid IS NOT NULL THEN bitmap_hash64_udf(r.event_id) END)) AS src_chl_new_order_pay_cnt,
    SUM(CASE WHEN chl.uid IS NOT NULL THEN r.amount ELSE 0 END) AS src_chl_new_order_pay_amt
  FROM dwd.dwd_order_paid_d r
  LEFT JOIN new_user_reg n
    ON r.dt = n.dt AND r.uid = n.uid AND r.app_id = n.app_id
  LEFT JOIN nat_new_user nat
    ON r.dt = nat.dt AND r.uid = nat.uid AND r.app_id = nat.app_id
  LEFT JOIN chl_new_user chl
    ON r.dt = chl.dt AND r.uid = chl.uid AND r.app_id = chl.app_id
  WHERE r.dt = '{{dt}}'
    {{app_filter}}
    AND r.order_type IN ('coin_purchase', 'vip_subscription')
    AND r.currency = 'CNY'
  GROUP BY r.dt, r.app_id
)
SELECT
  t.dt,
  t.app_id,
  t.order_pay_users,
  src.src_order_pay_users,
  t.order_pay_cnt,
  src.src_order_pay_cnt,
  t.order_pay_amt,
  src.src_order_pay_amt,
  t.new_order_pay_users,
  src.src_new_order_pay_users,
  t.new_order_pay_cnt,
  src.src_new_order_pay_cnt,
  t.new_order_pay_amt,
  src.src_new_order_pay_amt,
  t.old_order_pay_users,
  src.src_order_pay_users - src.src_new_order_pay_users AS src_old_order_pay_users,
  t.old_order_pay_cnt,
  src.src_order_pay_cnt - src.src_new_order_pay_cnt AS src_old_order_pay_cnt,
  t.old_order_pay_amt,
  src.src_order_pay_amt - src.src_new_order_pay_amt AS src_old_order_pay_amt,
  t.nat_new_order_pay_users,
  src.src_nat_new_order_pay_users,
  t.nat_new_order_pay_cnt,
  src.src_nat_new_order_pay_cnt,
  t.nat_new_order_pay_amt,
  src.src_nat_new_order_pay_amt,
  t.chl_new_order_pay_users,
  src.src_chl_new_order_pay_users,
  t.chl_new_order_pay_cnt,
  src.src_chl_new_order_pay_cnt,
  t.chl_new_order_pay_amt,
  src.src_chl_new_order_pay_amt
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(t.order_pay_users, 0) <> COALESCE(src.src_order_pay_users, 0)
    OR COALESCE(t.order_pay_cnt, 0) <> COALESCE(src.src_order_pay_cnt, 0)
    OR COALESCE(t.order_pay_amt, 0) <> COALESCE(src.src_order_pay_amt, 0)
    OR COALESCE(t.new_order_pay_users, 0) <> COALESCE(src.src_new_order_pay_users, 0)
    OR COALESCE(t.new_order_pay_cnt, 0) <> COALESCE(src.src_new_order_pay_cnt, 0)
    OR COALESCE(t.new_order_pay_amt, 0) <> COALESCE(src.src_new_order_pay_amt, 0)
    OR COALESCE(t.old_order_pay_users, 0) <> COALESCE(src.src_order_pay_users - src.src_new_order_pay_users, 0)
    OR COALESCE(t.old_order_pay_cnt, 0) <> COALESCE(src.src_order_pay_cnt - src.src_new_order_pay_cnt, 0)
    OR COALESCE(t.old_order_pay_amt, 0) <> COALESCE(src.src_order_pay_amt - src.src_new_order_pay_amt, 0)
    OR COALESCE(t.nat_new_order_pay_users, 0) <> COALESCE(src.src_nat_new_order_pay_users, 0)
    OR COALESCE(t.nat_new_order_pay_cnt, 0) <> COALESCE(src.src_nat_new_order_pay_cnt, 0)
    OR COALESCE(t.nat_new_order_pay_amt, 0) <> COALESCE(src.src_nat_new_order_pay_amt, 0)
    OR COALESCE(t.chl_new_order_pay_users, 0) <> COALESCE(src.src_chl_new_order_pay_users, 0)
    OR COALESCE(t.chl_new_order_pay_cnt, 0) <> COALESCE(src.src_chl_new_order_pay_cnt, 0)
    OR COALESCE(t.chl_new_order_pay_amt, 0) <> COALESCE(src.src_chl_new_order_pay_amt, 0)
  )
LIMIT 100;
```

#### part_02_04_retention_backfill_reconciliation
- 对应程序逻辑块：`target_dates`、`retention`
- 来源表：`ads.ads_user_retention_d`
- 目标字段：`day1_ret_cnt`、`day3_ret_cnt`、`day7_ret_cnt`
- 已确认口径：留存表 `dt` 是注册日，项目日报在主跑 `{{dt}}` 时，应同步把 `{{dt}} / {{dt-1}} / {{dt-3}} / {{dt-7}}` 这些注册日的成熟留存值一起写回到日报。
- 当前程序现状：已绑定 SQL 改为 `INSERT INTO` + `target_dates` 方案，脚本内直接纳入 `T / T-1 / T-3 / T-7` 的注册日集合，再按 `dt + app_id` 汇总留存后与其它来源合并写入。
- 已验证结论：已对 `2026-04-07` 的查询体做直接执行验证，输出同时覆盖 `2026-04-07 / 2026-04-06 / 2026-04-04 / 2026-03-31` 四个注册日，且 `(dt, app_id)` 唯一；抽样 app 的 `day1/day3/day7` 与 `ads.ads_user_retention_d` 聚合结果一致。
- 当前处理要求：`/datacheck` 应按“脚本内回填已实现”来核验，不再把留存回填缺口作为默认结论。
- 建议处理办法：日常校验时优先检查查询体是否同时产出 `T / T-1 / T-3 / T-7` 四个注册日，以及这些日期上 `day1/day3/day7` 是否与留存源表一致。

##### SQL：多天分布检查
```sql
SELECT
  dt,
  COUNT(*) AS total_rows,
  SUM(CASE WHEN COALESCE(day1_ret_cnt, 0) > 0 THEN 1 ELSE 0 END) AS day1_nonzero_rows,
  SUM(CASE WHEN COALESCE(day3_ret_cnt, 0) > 0 THEN 1 ELSE 0 END) AS day3_nonzero_rows,
  SUM(CASE WHEN COALESCE(day7_ret_cnt, 0) > 0 THEN 1 ELSE 0 END) AS day7_nonzero_rows
FROM ads.ads_user_retention_d
WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 10 DAY) AND '{{dt}}'
GROUP BY dt
ORDER BY dt;
```

##### SQL：按注册日多天对账
```sql
WITH src AS (
  SELECT
    dt,
    app_id,
    SUM(day1_ret_cnt) AS src_day1_ret_cnt,
    SUM(day3_ret_cnt) AS src_day3_ret_cnt,
    SUM(day7_ret_cnt) AS src_day7_ret_cnt
  FROM ads.ads_user_retention_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 10 DAY) AND '{{dt}}'
  GROUP BY dt, app_id
)
SELECT
  t.dt,
  COUNT(*) AS compare_rows,
  SUM(CASE WHEN COALESCE(t.day1_ret_cnt, 0) = COALESCE(src.src_day1_ret_cnt, 0) THEN 0 ELSE 1 END) AS day1_mismatch_rows,
  SUM(CASE WHEN COALESCE(t.day3_ret_cnt, 0) = COALESCE(src.src_day3_ret_cnt, 0) THEN 0 ELSE 1 END) AS day3_mismatch_rows,
  SUM(CASE WHEN COALESCE(t.day7_ret_cnt, 0) = COALESCE(src.src_day7_ret_cnt, 0) THEN 0 ELSE 1 END) AS day7_mismatch_rows
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 10 DAY) AND '{{dt}}'
GROUP BY t.dt
ORDER BY t.dt;
```

##### SQL：异常样本定位
```sql
WITH src AS (
  SELECT
    dt,
    app_id,
    SUM(day1_ret_cnt) AS src_day1_ret_cnt,
    SUM(day3_ret_cnt) AS src_day3_ret_cnt,
    SUM(day7_ret_cnt) AS src_day7_ret_cnt
  FROM ads.ads_user_retention_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 10 DAY) AND '{{dt}}'
  GROUP BY dt, app_id
)
SELECT
  t.dt,
  t.app_id,
  t.day1_ret_cnt,
  src.src_day1_ret_cnt,
  t.day3_ret_cnt,
  src.src_day3_ret_cnt,
  t.day7_ret_cnt,
  src.src_day7_ret_cnt
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 10 DAY) AND '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(t.day1_ret_cnt, 0) <> COALESCE(src.src_day1_ret_cnt, 0)
    OR COALESCE(t.day3_ret_cnt, 0) <> COALESCE(src.src_day3_ret_cnt, 0)
    OR COALESCE(t.day7_ret_cnt, 0) <> COALESCE(src.src_day7_ret_cnt, 0)
  )
ORDER BY t.dt, t.app_id
LIMIT 100;
```

#### part_02_05_channel_promotion_reconciliation
- 对应程序逻辑块：`channel_promo`
- 来源表：`ads.ads_channel_promotion_summary_d`
- 目标字段：`dl_page_view_cnt`、`dl_page_click_cnt`
- 已确认口径：
  - `dl_page_view_cnt` 取 `landing_page_view_num`
  - `dl_page_click_cnt` 取 `landing_page_click_num`
- 当前程序现状：已绑定 SQL 使用字段 `landing_page_click_num`，并已按当前规则完成来源核验。

##### SQL：来源对账
```sql
WITH src AS (
  SELECT
    CAST(date_key AS DATE) AS dt,
    app_id,
    SUM(landing_page_view_num) AS src_dl_page_view_cnt,
    SUM(landing_page_click_num) AS src_dl_page_click_cnt
  FROM ads.ads_channel_promotion_summary_d
  WHERE CAST(date_key AS DATE) = '{{dt}}'
    {{app_filter}}
  GROUP BY CAST(date_key AS DATE), app_id
)
SELECT
  t.dt,
  t.app_id,
  t.dl_page_view_cnt,
  src.src_dl_page_view_cnt,
  t.dl_page_click_cnt,
  src.src_dl_page_click_cnt
FROM ads.ads_product_day_stat_d t
LEFT JOIN src
  ON t.dt = src.dt AND t.app_id = src.app_id
WHERE t.dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(t.dl_page_view_cnt, 0) <> COALESCE(src.src_dl_page_view_cnt, 0)
    OR COALESCE(t.dl_page_click_cnt, 0) <> COALESCE(src.src_dl_page_click_cnt, 0)
  )
LIMIT 100;
```

#### part_02_06_effective_metrics_reconciliation
- 对应程序逻辑块：`effective_active`、`effective_metrics`、`new_user_reg`、`nat_new_user`、`chl_new_user`
- 来源表：`dwd.dwd_app_page_view_d`、`dwd.dwd_user_register_d_v2`、`dim.dim_user_all`
- 目标字段：`effective_dau_count`、`effective_old_dau_count`、`effective_new_reg_count`、`effective_chl_new_reg_count`、`effective_nat_new_reg_count`
- 已确认口径：
  - `effective_active` = `dwd.dwd_app_page_view_d` 当日按 `(dt, app_id, uid)` `COUNT(DISTINCT page_key) ≥ 2` 的 uid
  - `effective_dau_count` = `effective_active` 去重 uid 数
  - `effective_new_reg_count` = `effective_active ∩ new_user_reg`（当日新注册）
  - `effective_old_dau_count` = `effective_active ∖ new_user_reg`（当日活跃但非当日新注册）
  - `effective_nat_new_reg_count` = `effective_active ∩ nat_new_user`（自然注册，按 `dim.dim_user_all.register_channel = 'organic'`）
  - `effective_chl_new_reg_count` = `effective_active ∩ chl_new_user`（渠道注册）
- 关键规则：
  - 严格 `COUNT(DISTINCT page_key) ≥ 2`，过滤 `page_key IS NULL OR TRIM='' `
  - 渠道归一以 `dim.dim_user_all.register_channel` 为权威，fallback 到 `dwd.channel`
  - 守恒：`effective_dau = effective_new + effective_old` / `effective_new = effective_chl + effective_nat`

##### SQL：来源对账
```sql
WITH new_user_reg AS (
  SELECT DISTINCT dt, uid, app_id FROM dwd.dwd_user_register_d_v2 WHERE dt='{{dt}}'
),
nat_new_user AS (
  SELECT DISTINCT r.dt, r.uid, r.app_id FROM dwd.dwd_user_register_d_v2 r
  LEFT JOIN dim.dim_user_all d ON r.uid=d.uid AND r.app_id=d.app_id
  WHERE r.dt='{{dt}}' AND COALESCE(d.register_channel, r.channel, 'organic') = 'organic'
),
chl_new_user AS (
  SELECT DISTINCT r.dt, r.uid, r.app_id FROM dwd.dwd_user_register_d_v2 r
  LEFT JOIN dim.dim_user_all d ON r.uid=d.uid AND r.app_id=d.app_id
  WHERE r.dt='{{dt}}' AND COALESCE(d.register_channel, r.channel, 'organic') != 'organic'
),
effective_active AS (
  SELECT t.dt, t.app_id, t.uid FROM (
    SELECT dt, app_id, uid, COUNT(DISTINCT page_key) AS pk_cnt
    FROM dwd.dwd_app_page_view_d
    WHERE dt='{{dt}}' AND uid IS NOT NULL AND TRIM(uid) <> ''
      AND page_key IS NOT NULL AND TRIM(page_key) <> ''
    GROUP BY dt, app_id, uid
  ) t WHERE t.pk_cnt >= 2
),
src AS (
  SELECT ea.dt, ea.app_id,
    BITMAP_UNION_COUNT(TO_BITMAP(bitmap_hash64_udf(ea.uid))) AS src_eff_dau,
    BITMAP_UNION_COUNT(TO_BITMAP(IF(n.uid IS NOT NULL, bitmap_hash64_udf(ea.uid), NULL))) AS src_eff_new,
    BITMAP_UNION_COUNT(TO_BITMAP(IF(n.uid IS NULL, bitmap_hash64_udf(ea.uid), NULL))) AS src_eff_old,
    BITMAP_UNION_COUNT(TO_BITMAP(IF(nat.uid IS NOT NULL, bitmap_hash64_udf(ea.uid), NULL))) AS src_eff_nat,
    BITMAP_UNION_COUNT(TO_BITMAP(IF(chl.uid IS NOT NULL, bitmap_hash64_udf(ea.uid), NULL))) AS src_eff_chl
  FROM effective_active ea
  LEFT JOIN new_user_reg n ON ea.dt=n.dt AND ea.uid=n.uid AND ea.app_id=n.app_id
  LEFT JOIN nat_new_user nat ON ea.dt=nat.dt AND ea.uid=nat.uid AND ea.app_id=nat.app_id
  LEFT JOIN chl_new_user chl ON ea.dt=chl.dt AND ea.uid=chl.uid AND ea.app_id=chl.app_id
  GROUP BY ea.dt, ea.app_id
)
SELECT
  COUNT(*) rows_,
  SUM(CASE WHEN COALESCE(t.effective_dau_count,0)         <> COALESCE(s.src_eff_dau,0) THEN 1 ELSE 0 END) AS dau_mis,
  SUM(CASE WHEN COALESCE(t.effective_new_reg_count,0)     <> COALESCE(s.src_eff_new,0) THEN 1 ELSE 0 END) AS new_mis,
  SUM(CASE WHEN COALESCE(t.effective_old_dau_count,0)     <> COALESCE(s.src_eff_old,0) THEN 1 ELSE 0 END) AS old_mis,
  SUM(CASE WHEN COALESCE(t.effective_nat_new_reg_count,0) <> COALESCE(s.src_eff_nat,0) THEN 1 ELSE 0 END) AS nat_mis,
  SUM(CASE WHEN COALESCE(t.effective_chl_new_reg_count,0) <> COALESCE(s.src_eff_chl,0) THEN 1 ELSE 0 END) AS chl_mis
FROM ads.ads_product_day_stat_d t
LEFT JOIN src s ON t.dt=s.dt AND t.app_id=s.app_id
WHERE t.dt='{{dt}}';
```

### part_03_metric_sanity
- 目的：检查异常值、空值、不合理值
- 建议检查：
  - 不应出现负数
  - 若人数为 0，金额/笔数是否异常 > 0
  - 点击数是否大于访问数等
- 当前状态：先定义规则，后续可补 SQL

### part_04_exception_sampling
- 目的：对异常 app 做抽样输出，便于人工复核
- 默认输出：按异常程度排序的前若干条
- 可与 `part_01_total_vs_subtotal` 共用异常明细 SQL

## 4. 报告约定
- 结果报告目录：`.claude/database/reports/ads.ads_product_day_stat_d/`
- 建议文件名：
  - 无 app_id：`validate__{{dt}}__{{timestamp}}.md`
  - 有 app_id：`validate__{{dt}}__app_{{app_id}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：先写总体结论，明确总分核查与来源核查是否通过，以及核心问题
  2. 核查大类汇总：至少分别汇总“总分核查”“来源核查”的结果表格
  3. 逐条规则结果：每条规则都要列出核验范围、异常行数/异常样本数、结论
  4. 抽样证明：如规则通过，给正常样本；如规则失败，同时给异常样本
  5. 问题与处理建议：针对异常规则给出可执行处理办法，并说明建议依据
- 报告中的所有结论都应带数据，不能只写口头判断。

## 5. 剧本维护约定
- 该剧本默认绑定 `/Users/arthur/Program/datacenter/dc-parent/ops_system/05.ads/job_ads_product_day_stat_d/ads_product_day_stat_d.sql`。
- 当处理程序中的来源表、连接键、过滤条件、聚合逻辑、关键字段映射变更时，必须同步更新本剧本。
- 若只是程序结构重构但业务口径未变，至少同步更新“绑定程序”章节与对应逻辑块说明。
- 若剧本与程序或业务确认口径不一致，必须显式记录“待核对点”，不能静默覆盖。
