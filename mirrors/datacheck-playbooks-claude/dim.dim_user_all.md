# dim.dim_user_all 用户状态表核查剧本

## 1. 表信息
- 目标表：`dim.dim_user_all`
- 业务名：用户状态总表（状态字段，累计金额指标已拆出至 `dws.dws_user_finance_d`）
- 状态：重构后首次上线
- 表说明：每个 `(app_id, uid)` 一行，承载身份/渠道/生命周期阶段/最近一次各类行为的时刻与金额
- 关键说明：
  - 主键 `(app_id, uid)`
  - `row_update_time` 为行级数据加入/更新时间，下游对账/跑批按此字段切片
  - `register_channel` 一次写入不覆盖（注册当时的原始 channel）
  - `register_time` / `first_recharge_*` / `is_multi_recharge_user_time` / `create_time` 一次定终身
  - `lifecycle_stage` 只在 daily 跑批时刷新，取值：`abandoned` / `new` / `active` / `dormant` / `churned`

## 2. 参数约定
- 必填：`dt`（核查截至日期；一般传昨天）
- 选填：`app_code` / `app_id`、`uid`、`user_type`、`lifecycle_stage`
- `dt` 语义：验证"截至 dt 日收盘后的 dim_user_all 状态"

## 3. 绑定程序
- DDL：`ops_system/06.dim/job_dim_user_type_d/dim_user_all_ddl.sql`
- 小时 ETL：`ops_system/06.dim/job_dim_user_type_d/dim_user_all_hourly.sql`
- 日终 ETL：`ops_system/06.dim/job_dim_user_type_d/dim_user_all_daily.sql`
- 数据来源表：
  - `dwd.dwd_user_register_d_v2`（注册事件）
  - `dwd.dwd_app_page_view_d`（活跃 / user_type / 位置 / 设备）
  - `dwd.dwd_user_login_d_v2`（登录时刻）
  - `dwd.dwd_order_paid_d`（充值相关时刻 / 金额 / 渠道兜底）
- 关键逻辑块：
  - 小时 ETL：对本 slot 活跃用户做 UPSERT；`register_channel` 只在新用户分支写；`lifecycle_stage` 不变；`last_recharge_*` 本 slot 有充值则覆盖
  - 日终 ETL：T-1 全量重算；刷新 `lifecycle_stage`、补齐首充/末次行为时刻
- 程序维护约定：若来源表、lifecycle_stage 规则、channel 收口规则、首充/末次字段语义变化，必须同步更新本剧本

## 4. 核查 parts

### part_01_basic_shape_and_uniqueness
- 目的：基础形态、主键唯一、关键字段非空与值域合法
- 来源表：`dim.dim_user_all`
- 核查重点：
  - 主键 `(app_id, uid)` 唯一
  - `app_id` / `uid` 非空
  - `device` 落在 `IOS / ANDROID / PC / OTHER / 其他 / unknown` 允许集（注：历史旧值可能为 `android/ios/pc` 小写）
  - `lifecycle_stage` 落在 `new / active / dormant / churned / abandoned` 中（首次部署后可能存在 NULL，标记为风险项）
  - `user_type` 落在 `normal / vip`
  - `register_time` 非空（或等于兜底 `2025-12-20 00:00:00`）
- 判定：主键冲突或核心字段非法 → 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_id) AS app_cnt,
  COUNT(DISTINCT uid) AS uid_cnt,
  SUM(CASE WHEN lifecycle_stage IS NULL THEN 1 ELSE 0 END) AS null_lifecycle,
  SUM(CASE WHEN register_channel IS NULL THEN 1 ELSE 0 END) AS null_register_channel,
  SUM(CASE WHEN last_active_time IS NULL THEN 1 ELSE 0 END) AS null_last_active,
  SUM(CASE WHEN row_update_time IS NULL THEN 1 ELSE 0 END) AS null_row_update_time,
  MIN(row_update_time) AS min_row_update_time,
  MAX(row_update_time) AS max_row_update_time
FROM dim.dim_user_all
  {{app_filter}};
```

#### SQL：主键唯一性
```sql
SELECT app_id, uid, COUNT(*) AS cnt
FROM dim.dim_user_all
  {{app_filter}}
GROUP BY app_id, uid
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：枚举值合法性
```sql
SELECT 'device_invalid' AS rule, device AS val, COUNT(*) AS cnt
FROM dim.dim_user_all
WHERE device NOT IN ('IOS','ANDROID','PC','OTHER','其他','unknown','android','ios','pc')
  {{app_filter}}
GROUP BY device
UNION ALL
SELECT 'lifecycle_invalid', lifecycle_stage, COUNT(*)
FROM dim.dim_user_all
WHERE lifecycle_stage IS NOT NULL
  AND lifecycle_stage NOT IN ('new','active','dormant','churned','abandoned')
  {{app_filter}}
GROUP BY lifecycle_stage
UNION ALL
SELECT 'user_type_invalid', user_type, COUNT(*)
FROM dim.dim_user_all
WHERE user_type IS NOT NULL AND user_type NOT IN ('normal','vip','NORMAL','VIP')
  {{app_filter}}
GROUP BY user_type
LIMIT 100;
```

### part_02_lifecycle_stage_rule_verification
- 目的：验证 `lifecycle_stage` 规则的正确性
- 判定：每条规则不符合预期的样本应 < 1% 或为 0
- 规则对照（截至 `{{dt}}`）：

| lifecycle_stage | 预期条件 |
|---|---|
| abandoned | `abandoned_tag IS NOT NULL` |
| new | `DATEDIFF({{dt}}, register_time) <= 7` |
| active | `DATEDIFF({{dt}}, last_active_time) <= 7`（且非 new） |
| dormant | `DATEDIFF({{dt}}, last_active_time) BETWEEN 8 AND 30` |
| churned | `DATEDIFF({{dt}}, last_active_time) > 30` 或 `last_active_time IS NULL` |

#### SQL：规则冲突样本
```sql
SELECT
  lifecycle_stage,
  DATEDIFF(CAST('{{dt}}' AS DATE), CAST(register_time AS DATE)) AS reg_age_days,
  DATEDIFF(CAST('{{dt}}' AS DATE), CAST(last_active_time AS DATE)) AS active_age_days,
  abandoned_tag,
  COUNT(*) AS cnt
FROM dim.dim_user_all
  {{app_filter}}
WHERE NOT (
  (lifecycle_stage = 'abandoned' AND abandoned_tag IS NOT NULL)
  OR (lifecycle_stage = 'new' AND DATEDIFF(CAST('{{dt}}' AS DATE), CAST(register_time AS DATE)) <= 7 AND abandoned_tag IS NULL)
  OR (lifecycle_stage = 'active' AND DATEDIFF(CAST('{{dt}}' AS DATE), CAST(last_active_time AS DATE)) <= 7 AND abandoned_tag IS NULL AND DATEDIFF(CAST('{{dt}}' AS DATE), CAST(register_time AS DATE)) > 7)
  OR (lifecycle_stage = 'dormant' AND DATEDIFF(CAST('{{dt}}' AS DATE), CAST(last_active_time AS DATE)) BETWEEN 8 AND 30 AND abandoned_tag IS NULL)
  OR (lifecycle_stage = 'churned' AND (last_active_time IS NULL OR DATEDIFF(CAST('{{dt}}' AS DATE), CAST(last_active_time AS DATE)) > 30) AND abandoned_tag IS NULL)
)
GROUP BY lifecycle_stage, reg_age_days, active_age_days, abandoned_tag
LIMIT 100;
```

#### SQL：按 app 分布
```sql
SELECT app_id, lifecycle_stage, COUNT(*) AS cnt
FROM dim.dim_user_all
  {{app_filter}}
GROUP BY app_id, lifecycle_stage
ORDER BY app_id, lifecycle_stage;
```

### part_03_once_written_fields_stability
- 目的：验证"一次写入不覆盖"字段的稳定性
- 字段：`register_channel` / `register_time` / `first_recharge_time` / `first_recharge_amount` / `first_recharge_type` / `is_multi_recharge_user_time` / `create_time`
- 判定：
  - `register_time` 和 `dwd.dwd_user_register_d_v2` 按 (app_id, uid) 最早 event_time 一致（允许 organic 优先逻辑差异）
  - `first_recharge_time` 和 `dwd.dwd_order_paid_d` 按 (app_id, uid) 最早 event_time 一致
  - `first_recharge_amount` / `first_recharge_type` 对应该最早记录的 `amount` / `order_type`

#### SQL：register_time 对账（抽样 uid）
```sql
WITH src AS (
  SELECT app_id, uid,
         MIN_BY(channel, CASE WHEN channel='organic' THEN 1 ELSE 0 END * 1000000 + UNIX_TIMESTAMP(event_time)) AS src_register_channel,
         MIN(event_time) AS src_earliest_register_time
  FROM dwd.dwd_user_register_d_v2
  WHERE app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid,
       t.register_time AS tgt_register_time, src.src_earliest_register_time,
       t.register_channel AS tgt_register_channel, src.src_register_channel
FROM dim.dim_user_all t
INNER JOIN src ON t.app_id = src.app_id AND t.uid = src.uid
WHERE t.register_time <> src.src_earliest_register_time
   OR (t.register_channel IS NOT NULL AND t.register_channel <> src.src_register_channel)
LIMIT 100;
```

#### SQL：first_recharge_* 对账（抽样 uid）
```sql
WITH src AS (
  SELECT app_id, uid,
         MIN(event_time) AS src_first_time,
         MIN_BY(amount, event_time) AS src_first_amount,
         MIN_BY(order_type, event_time) AS src_first_type
  FROM dwd.dwd_order_paid_d
  WHERE app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid,
       t.first_recharge_time, src.src_first_time,
       t.first_recharge_amount, src.src_first_amount,
       t.first_recharge_type, src.src_first_type
FROM dim.dim_user_all t
INNER JOIN src ON t.app_id = src.app_id AND t.uid = src.uid
WHERE COALESCE(t.first_recharge_time, '1970-01-01') <> src.src_first_time
   OR COALESCE(t.first_recharge_amount, -1) <> src.src_first_amount
   OR COALESCE(t.first_recharge_type, '') <> src.src_first_type
LIMIT 100;
```

### part_04_latest_fields_reconciliation
- 目的：最近一次行为字段与 dwd 源对账
- 字段：`last_login_time` / `last_active_time` / `last_recharge_time` / `last_recharge_amount` / `last_recharge_type` / `last_vip_time`
- 判定：差异样本 = 0；允许 dim 值 >= 源值（因为 daily 跑批时可能源表又追加了数据）

#### SQL：last_* 字段对账
```sql
WITH login AS (
  SELECT app_id, uid, MAX(event_time) AS src_last_login
  FROM dwd.dwd_user_login_d_v2
  WHERE app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
),
active AS (
  SELECT app_id, uid, MAX(event_time) AS src_last_active
  FROM dwd.dwd_app_page_view_d
  WHERE app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
),
recharge AS (
  SELECT app_id, uid,
         MAX(event_time) AS src_last_recharge,
         MAX_BY(amount, event_time) AS src_last_amount,
         MAX_BY(order_type, event_time) AS src_last_type
  FROM dwd.dwd_order_paid_d
  WHERE app_id IS NOT NULL AND uid IS NOT NULL
    {{app_filter}}
  GROUP BY app_id, uid
)
SELECT t.app_id, t.uid,
       t.last_login_time, login.src_last_login,
       t.last_active_time, active.src_last_active,
       t.last_recharge_time, recharge.src_last_recharge,
       t.last_recharge_amount, recharge.src_last_amount,
       t.last_recharge_type, recharge.src_last_type
FROM dim.dim_user_all t
LEFT JOIN login    ON t.app_id = login.app_id    AND t.uid = login.uid
LEFT JOIN active   ON t.app_id = active.app_id   AND t.uid = active.uid
LEFT JOIN recharge ON t.app_id = recharge.app_id AND t.uid = recharge.uid
WHERE COALESCE(t.last_login_time, '1970-01-01')    <> COALESCE(login.src_last_login, '1970-01-01')
   OR COALESCE(t.last_active_time, '1970-01-01')   <> COALESCE(active.src_last_active, '1970-01-01')
   OR COALESCE(t.last_recharge_time, '1970-01-01') <> COALESCE(recharge.src_last_recharge, '1970-01-01')
   OR COALESCE(t.last_recharge_amount, -1)         <> COALESCE(recharge.src_last_amount, -1)
   OR COALESCE(t.last_recharge_type, '')           <> COALESCE(recharge.src_last_type, '')
  {{app_filter}}
LIMIT 100;
```

### part_05_row_update_time_sanity
- 目的：验证 `row_update_time` 切片对账的可用性
- 判定：
  - 所有行 `row_update_time` 非空
  - 最大 `row_update_time` 应等于"最近一次跑批结束时间"
  - 同一批次（hourly 或 daily）写入的行，`row_update_time` 应一致

#### SQL：row_update_time 分布
```sql
SELECT
  row_update_time,
  COUNT(*) AS rows_with_this_batch_time
FROM dim.dim_user_all
  {{app_filter}}
GROUP BY row_update_time
ORDER BY row_update_time DESC
LIMIT 30;
```

### part_06_exception_sampling_and_reporting
- 目的：统一输出异常样本
- 必含内容：
  - 主键重复样本（若有）
  - lifecycle_stage 规则冲突样本
  - register_time / first_recharge_* 对账异常样本
  - last_* 对账异常样本
  - null_register_channel 数量 / 占比（首次部署后通常较高，作为历史回刷入口）
- 判定：说明性输出

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dim.dim_user_all/`
- 文件名：`validate__{{dt}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：整体是否通过、失败 part 名称
  2. 核查大类汇总：基础形态、lifecycle_stage 规则、一次定终身字段、最近行为字段、row_update_time 一致性
  3. 逐条规则：核验范围（总行数 / 按 app 行数）、异常量 / 样本量、结论
  4. 问题与处理建议：区分"首次部署特性"（如 null_register_channel）、"程序 bug"、"数据漂移"
  5. 所有结论带数据，不仅口头判断

## 6. 剧本维护约定
- 若 DDL 或 ETL 的字段语义、lifecycle_stage 规则、channel 收口逻辑、首充判定、最近行为判定发生变化，必须同步更新本剧本
- 下游 ETL 改造成"带 cutoff 切片对账"后，新增一个 part 验证"同 cutoff 下 dim_user_all 和重算一致"
