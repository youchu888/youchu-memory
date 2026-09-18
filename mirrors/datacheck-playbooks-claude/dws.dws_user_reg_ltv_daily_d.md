# dws.dws_user_reg_ltv_daily_d 核查剧本

## 1. 表信息
- 表名：`dws.dws_user_reg_ltv_daily_d`
- 业务名：用户生命价值
- 状态：上线
- 表说明：按注册 cohort 沉淀 app 用户从注册当天到注册后第 30 天的充值金额事实表
- 目标粒度：`dt + app_code + channel + region + device`
- 核心指标：`new_users`、`day_0_pay_amount`、`day_1_pay_amount`、`day_2_pay_amount`、`day_3_pay_amount`、`day_4_pay_amount`、`day_5_pay_amount`、`day_6_pay_amount`、`day_7_pay_amount`、`day_8_pay_amount`、`day_9_pay_amount`、`day_10_pay_amount`、`day_11_pay_amount`、`day_12_pay_amount`、`day_13_pay_amount`、`day_14_pay_amount`、`day_15_pay_amount`、`day_16_pay_amount`、`day_17_pay_amount`、`day_18_pay_amount`、`day_19_pay_amount`、`day_20_pay_amount`、`day_21_pay_amount`、`day_22_pay_amount`、`day_23_pay_amount`、`day_24_pay_amount`、`day_25_pay_amount`、`day_26_pay_amount`、`day_27_pay_amount`、`day_28_pay_amount`、`day_29_pay_amount`、`day_30_pay_amount`
- 关键说明：
  - `new_users` 表示注册当天的新增用户数，当前版本只和注册来源对账，不依赖用户模型联查
  - `day_N_pay_amount` 表示注册后第 N 天充值金额
  - 未成熟 `day_N_pay_amount` 应保持 `NULL`
  - 当前程序使用 `SUM(DISTINCT au.amount)`，存在把同 cohort 下同金额不同订单误去重的风险，必须专项核查

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_code` / `app_id`、`channel`、`region`、`device`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该注册日全量 app 的全维度结果
  - 传 `dt + app_code/app_id`：核查指定 app
  - 其他维度参数仅用于下钻，不改变最终对账粒度规则

## 3. 绑定程序
- 绑定处理程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_user_reg_ltv_daily_d/dws_user_reg_ltv_daily_d.sql`
- 当前绑定说明：`/datacheck` 执行用户生命价值核查时，默认以该 SQL 的已登记实现为程序参考；当前版本先校验来源口径与成熟日逻辑，不要求用户模型联查。
- 关键逻辑块：
  - `register`：按 `dt + app_id + uid` 取首条注册记录，完成 cohort 去重、设备归一、地区映射
  - `active_user`：提取支付事实，仅统计 `vip_subscription / coin_purchase` 且 `event='order_paid'`
  - 最终 `GROUP BY`：按 `dt + app_id + channel + region + device` 输出 `new_users + day_0~day_30_pay_amount`
- 已确认逻辑：
  - 注册去重规则：`ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time)`
  - 地区映射：`dim.dim_region_info_all`
  - 设备归一：`IOS / ANDROID / PC / OTHER`
  - 成熟日规则：未到成熟日的 `day_N_pay_amount` 应保持 `NULL`
- 程序维护约定：若注册去重、地区映射、设备归一、支付过滤、金额聚合逻辑或成熟日出值规则变化，必须同步更新本剧本与 `.claude/database/knowledge.md`

## 4. 核查 parts

### part_01_basic_shape_and_sanity
- 目的：确认目标表基础形态、主键唯一性、空值、越界值与成熟日出值逻辑是否正常
- 来源表：`dws.dws_user_reg_ltv_daily_d`
- 核查重点：
  - 指定日期是否有数据
  - 主键 `dt + app_code + channel + region + device` 是否唯一
  - 主键字段是否为空
  - `device` 是否仅出现 `IOS / ANDROID / PC / OTHER`
  - `new_users` 与各 `day_N_pay_amount` 是否出现负值
  - 未成熟日期是否被错误写成 0 或非空值
- 判定：任一关键字段为空、负值、主键重复或未成熟日期误出值，则该 part 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(new_users) AS total_new_users,
  SUM(day_0_pay_amount) AS total_day_0_pay_amount,
  SUM(day_1_pay_amount) AS total_day_1_pay_amount,
  SUM(day_7_pay_amount) AS total_day_7_pay_amount,
  SUM(day_30_pay_amount) AS total_day_30_pay_amount
FROM dws.dws_user_reg_ltv_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}};
```

#### SQL：主键重复检查
```sql
SELECT
  dt,
  app_code,
  channel,
  region,
  device,
  COUNT(*) AS dup_cnt
FROM dws.dws_user_reg_ltv_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
GROUP BY dt, app_code, channel, region, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：空值、值域与负值检查
```sql
SELECT *
FROM dws.dws_user_reg_ltv_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  AND (
    app_code IS NULL
    OR channel IS NULL
    OR region IS NULL
    OR device IS NULL
    OR COALESCE(device, '__NULL__') NOT IN ('IOS', 'ANDROID', 'PC', 'OTHER')
    OR COALESCE(new_users, 0) < 0
    OR COALESCE(day_0_pay_amount, 0) < 0
    OR COALESCE(day_1_pay_amount, 0) < 0
    OR COALESCE(day_2_pay_amount, 0) < 0
    OR COALESCE(day_3_pay_amount, 0) < 0
    OR COALESCE(day_4_pay_amount, 0) < 0
    OR COALESCE(day_5_pay_amount, 0) < 0
    OR COALESCE(day_6_pay_amount, 0) < 0
    OR COALESCE(day_7_pay_amount, 0) < 0
    OR COALESCE(day_8_pay_amount, 0) < 0
    OR COALESCE(day_9_pay_amount, 0) < 0
    OR COALESCE(day_10_pay_amount, 0) < 0
    OR COALESCE(day_11_pay_amount, 0) < 0
    OR COALESCE(day_12_pay_amount, 0) < 0
    OR COALESCE(day_13_pay_amount, 0) < 0
    OR COALESCE(day_14_pay_amount, 0) < 0
    OR COALESCE(day_15_pay_amount, 0) < 0
    OR COALESCE(day_16_pay_amount, 0) < 0
    OR COALESCE(day_17_pay_amount, 0) < 0
    OR COALESCE(day_18_pay_amount, 0) < 0
    OR COALESCE(day_19_pay_amount, 0) < 0
    OR COALESCE(day_20_pay_amount, 0) < 0
    OR COALESCE(day_21_pay_amount, 0) < 0
    OR COALESCE(day_22_pay_amount, 0) < 0
    OR COALESCE(day_23_pay_amount, 0) < 0
    OR COALESCE(day_24_pay_amount, 0) < 0
    OR COALESCE(day_25_pay_amount, 0) < 0
    OR COALESCE(day_26_pay_amount, 0) < 0
    OR COALESCE(day_27_pay_amount, 0) < 0
    OR COALESCE(day_28_pay_amount, 0) < 0
    OR COALESCE(day_29_pay_amount, 0) < 0
    OR COALESCE(day_30_pay_amount, 0) < 0
  )
LIMIT 100;
```

#### SQL：未成熟日期误出值检查
```sql
SELECT *
FROM dws.dws_user_reg_ltv_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  AND (
    (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) AND day_1_pay_amount IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY) AND day_2_pay_amount IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) AND day_3_pay_amount IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND day_7_pay_amount IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND day_30_pay_amount IS NOT NULL)
  )
LIMIT 100;
```

### part_02_full_grain_source_reconciliation
- 目的：按真实处理逻辑做全维度来源重算与目标对账
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_order_paid_d`、`dim.dim_region_info_all`
- 最终对齐粒度：`dt + app_code + channel + region + device`
- 目标字段：`new_users`、`day_0_pay_amount ~ day_30_pay_amount`
- 关键规则：
  - 最终正确性只能按全维度判断
  - 注册 cohort 必须先做首条注册去重
  - 支付金额重算时不能使用 `SUM(DISTINCT amount)`，应先按订单唯一键聚合再求和
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：全维度来源重算
```sql
WITH register_base AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    t1.uid,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    COALESCE(d.region, 99999999) AS region
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
  ) t1
  LEFT JOIN dim.dim_region_info_all d
    ON t1.country = d.country_name
   AND t1.province = d.province_name
   AND t1.city = d.city_name
  WHERE t1.rn = 1
),
pay_base AS (
  SELECT
    dt,
    app_id,
    channel,
    uid,
    order_id,
    amount
  FROM dwd.dwd_order_paid_d
  WHERE dt BETWEEN '{{dt}}' AND DATE_ADD('{{dt}}', INTERVAL 30 DAY)
    AND order_type IN ('vip_subscription', 'coin_purchase')
    AND event = 'order_paid'
    {{app_filter}}
),
src AS (
  SELECT
    rb.dt,
    rb.app_code,
    rb.channel,
    rb.region,
    rb.device,
    COUNT(DISTINCT rb.uid) AS src_new_users,
    SUM(CASE WHEN pb.dt = rb.dt THEN pb.amount ELSE 0 END) AS src_day_0_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 1 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_1_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 2 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_2_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 3 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_3_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 4 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 4 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_4_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 5 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_5_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 6 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 6 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_6_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 7 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_7_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 8 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 8 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_8_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 9 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 9 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_9_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 10 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 10 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_10_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 11 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 11 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_11_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 12 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 12 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_12_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 13 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 13 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_13_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 14 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_14_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 15 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_15_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 16 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 16 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_16_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 17 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 17 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_17_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 18 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 18 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_18_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 19 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 19 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_19_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 20 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 20 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_20_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 21 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_21_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 22 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 22 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_22_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 23 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 23 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_23_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 24 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 24 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_24_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 25 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 25 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_25_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 26 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 26 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_26_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 27 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 27 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_27_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 28 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_28_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 29 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 29 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_29_pay_amount,
    CASE WHEN rb.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) THEN SUM(CASE WHEN pb.dt = DATE_ADD(rb.dt, INTERVAL 30 DAY) THEN pb.amount ELSE 0 END) ELSE NULL END AS src_day_30_pay_amount
  FROM register_base rb
  LEFT JOIN pay_base pb
    ON rb.app_code = pb.app_id
   AND rb.channel = pb.channel
   AND rb.uid = pb.uid
  GROUP BY rb.dt, rb.app_code, rb.channel, rb.region, rb.device
)
SELECT *
FROM src;
```

#### SQL：全维度来源对账异常明细
```sql
WITH src AS (
  -- 将上一段“全维度来源重算”SQL 放在这里
),
tgt AS (
  SELECT *
  FROM dws.dws_user_reg_ltv_daily_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
)
SELECT
  COALESCE(tgt.dt, src.dt) AS dt,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  tgt.new_users, src.src_new_users,
  tgt.day_0_pay_amount, src.src_day_0_pay_amount,
  tgt.day_1_pay_amount, src.src_day_1_pay_amount,
  tgt.day_7_pay_amount, src.src_day_7_pay_amount,
  tgt.day_30_pay_amount, src.src_day_30_pay_amount
FROM tgt
FULL OUTER JOIN src
  ON tgt.dt = src.dt
 AND tgt.app_code = src.app_code
 AND tgt.channel = src.channel
 AND tgt.region = src.region
 AND tgt.device = src.device
WHERE
  COALESCE(tgt.new_users, -1) <> COALESCE(src.src_new_users, -1)
  OR COALESCE(tgt.day_0_pay_amount, -1) <> COALESCE(src.src_day_0_pay_amount, -1)
  OR COALESCE(tgt.day_1_pay_amount, -1) <> COALESCE(src.src_day_1_pay_amount, -1)
  OR COALESCE(tgt.day_2_pay_amount, -1) <> COALESCE(src.src_day_2_pay_amount, -1)
  OR COALESCE(tgt.day_3_pay_amount, -1) <> COALESCE(src.src_day_3_pay_amount, -1)
  OR COALESCE(tgt.day_4_pay_amount, -1) <> COALESCE(src.src_day_4_pay_amount, -1)
  OR COALESCE(tgt.day_5_pay_amount, -1) <> COALESCE(src.src_day_5_pay_amount, -1)
  OR COALESCE(tgt.day_6_pay_amount, -1) <> COALESCE(src.src_day_6_pay_amount, -1)
  OR COALESCE(tgt.day_7_pay_amount, -1) <> COALESCE(src.src_day_7_pay_amount, -1)
  OR COALESCE(tgt.day_8_pay_amount, -1) <> COALESCE(src.src_day_8_pay_amount, -1)
  OR COALESCE(tgt.day_9_pay_amount, -1) <> COALESCE(src.src_day_9_pay_amount, -1)
  OR COALESCE(tgt.day_10_pay_amount, -1) <> COALESCE(src.src_day_10_pay_amount, -1)
  OR COALESCE(tgt.day_11_pay_amount, -1) <> COALESCE(src.src_day_11_pay_amount, -1)
  OR COALESCE(tgt.day_12_pay_amount, -1) <> COALESCE(src.src_day_12_pay_amount, -1)
  OR COALESCE(tgt.day_13_pay_amount, -1) <> COALESCE(src.src_day_13_pay_amount, -1)
  OR COALESCE(tgt.day_14_pay_amount, -1) <> COALESCE(src.src_day_14_pay_amount, -1)
  OR COALESCE(tgt.day_15_pay_amount, -1) <> COALESCE(src.src_day_15_pay_amount, -1)
  OR COALESCE(tgt.day_16_pay_amount, -1) <> COALESCE(src.src_day_16_pay_amount, -1)
  OR COALESCE(tgt.day_17_pay_amount, -1) <> COALESCE(src.src_day_17_pay_amount, -1)
  OR COALESCE(tgt.day_18_pay_amount, -1) <> COALESCE(src.src_day_18_pay_amount, -1)
  OR COALESCE(tgt.day_19_pay_amount, -1) <> COALESCE(src.src_day_19_pay_amount, -1)
  OR COALESCE(tgt.day_20_pay_amount, -1) <> COALESCE(src.src_day_20_pay_amount, -1)
  OR COALESCE(tgt.day_21_pay_amount, -1) <> COALESCE(src.src_day_21_pay_amount, -1)
  OR COALESCE(tgt.day_22_pay_amount, -1) <> COALESCE(src.src_day_22_pay_amount, -1)
  OR COALESCE(tgt.day_23_pay_amount, -1) <> COALESCE(src.src_day_23_pay_amount, -1)
  OR COALESCE(tgt.day_24_pay_amount, -1) <> COALESCE(src.src_day_24_pay_amount, -1)
  OR COALESCE(tgt.day_25_pay_amount, -1) <> COALESCE(src.src_day_25_pay_amount, -1)
  OR COALESCE(tgt.day_26_pay_amount, -1) <> COALESCE(src.src_day_26_pay_amount, -1)
  OR COALESCE(tgt.day_27_pay_amount, -1) <> COALESCE(src.src_day_27_pay_amount, -1)
  OR COALESCE(tgt.day_28_pay_amount, -1) <> COALESCE(src.src_day_28_pay_amount, -1)
  OR COALESCE(tgt.day_29_pay_amount, -1) <> COALESCE(src.src_day_29_pay_amount, -1)
  OR COALESCE(tgt.day_30_pay_amount, -1) <> COALESCE(src.src_day_30_pay_amount, -1)
LIMIT 100;
```

### part_03_registration_dedup_validation
- 目的：专项校验 `new_users` 的注册首条去重口径
- 来源表：`dwd.dwd_user_register_d_v2`、`dim.dim_region_info_all`
- 对齐粒度：`dt + app_code + channel + region + device`
- 关键规则：
  - 必须按 `dt + app_id + uid` 取首条注册记录
  - 当前版本只和注册来源核对，不和用户模型联查
- 判定：任一 `new_users` 不一致，则该 part 失败

#### SQL：新增用户来源重算
```sql
WITH register_base AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    t1.uid,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    COALESCE(d.region, 99999999) AS region
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
  ) t1
  LEFT JOIN dim.dim_region_info_all d
    ON t1.country = d.country_name
   AND t1.province = d.province_name
   AND t1.city = d.city_name
  WHERE t1.rn = 1
)
SELECT
  dt,
  app_code,
  channel,
  region,
  device,
  COUNT(DISTINCT uid) AS src_new_users
FROM register_base
GROUP BY dt, app_code, channel, region, device;
```

#### SQL：重复注册样本
```sql
SELECT *
FROM (
  SELECT
    dt,
    app_id,
    uid,
    channel,
    event_time,
    ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time) AS rn
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    {{app_filter}}
) t
WHERE rn > 1
LIMIT 100;
```

### part_04_payment_amount_validation
- 目的：专项校验支付金额来源与 `SUM(DISTINCT amount)` 风险
- 来源表：`dwd.dwd_order_paid_d`
- 对齐粒度：`dt + app_code + channel + region + device`
- 关键规则：
  - 仅统计 `order_type in ('vip_subscription','coin_purchase') AND event = 'order_paid'`
  - 应按订单唯一键聚合后再求和，不能用 `SUM(DISTINCT amount)` 代替订单去重
- 判定：若发现同 cohort 下同金额多订单，或来源重算与目标不一致，则该 part 失败

#### SQL：同金额多订单风险样本
```sql
WITH register_base AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    t1.uid,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    COALESCE(d.region, 99999999) AS region
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
  ) t1
  LEFT JOIN dim.dim_region_info_all d
    ON t1.country = d.country_name
   AND t1.province = d.province_name
   AND t1.city = d.city_name
  WHERE t1.rn = 1
)
SELECT
  rb.dt,
  rb.app_code,
  rb.channel,
  rb.region,
  rb.device,
  op.dt AS pay_dt,
  op.amount,
  COUNT(DISTINCT op.order_id) AS same_amount_order_cnt,
  COUNT(DISTINCT op.uid) AS same_amount_user_cnt
FROM register_base rb
INNER JOIN dwd.dwd_order_paid_d op
  ON rb.app_code = op.app_id
 AND rb.channel = op.channel
 AND rb.uid = op.uid
WHERE op.dt BETWEEN '{{dt}}' AND DATE_ADD('{{dt}}', INTERVAL 30 DAY)
  AND op.order_type IN ('vip_subscription', 'coin_purchase')
  AND op.event = 'order_paid'
GROUP BY rb.dt, rb.app_code, rb.channel, rb.region, rb.device, op.dt, op.amount
HAVING COUNT(DISTINCT op.order_id) > 1
LIMIT 100;
```

#### SQL：支付过滤异常样本
```sql
SELECT *
FROM dwd.dwd_order_paid_d
WHERE dt BETWEEN '{{dt}}' AND DATE_ADD('{{dt}}', INTERVAL 30 DAY)
  {{app_filter}}
  AND (
    event <> 'order_paid'
    OR order_type NOT IN ('vip_subscription', 'coin_purchase')
  )
LIMIT 100;
```

### part_05_exception_sampling
- 目的：统一输出异常样本，便于开发回归后快速复核
- 必含内容：
  - 主键重复样本
  - 全维度来源对账异常样本
  - 注册重复样本
  - 同金额多订单风险样本
  - 未成熟误出值样本
- 判定：说明性输出，不单独判失败；其结论依赖前述 parts

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_user_reg_ltv_daily_d/`
- 建议文件名：
  - 无 app 过滤：`validate__{{dt}}__{{timestamp}}.md`
  - 有 app 过滤：`validate__{{dt}}__app_{{app_code}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：明确“全维度来源核对是否通过”
  2. 核查大类汇总：基础形态、来源对账、注册去重、支付金额风险、异常样本
  3. 逐条规则结果：每条规则要给出核验范围、异常行数/样本数、结论
  4. 问题与处理建议：区分注册去重错误、金额 distinct 风险、成熟日出值错误、普通来源 mismatch
  5. 核心说明：当前版本的 `new_users` 只和注册来源校对，不依赖用户模型
- 报告中的所有结论都应带数据，不能只写口头判断

## 6. 剧本维护约定
- 该剧本默认绑定 `/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_user_reg_ltv_daily_d/dws_user_reg_ltv_daily_d.sql`
- 若注册首条去重、地区映射、设备归一、支付过滤条件、金额聚合逻辑或成熟日出值规则发生变化，必须同步更新本剧本
- 若后续用户模型已完成稳定核对，可补充 `new_users` 与用户模型的交叉回归项，但不能替代当前来源对账结论
