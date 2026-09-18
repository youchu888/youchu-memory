# dws.dws_user_first_recharge_retention_d 核查剧本

## 1. 表信息
- 表名：`dws.dws_user_first_recharge_retention_d`
- 业务名：首充留存模型表
- 状态：上线
- 表说明：按首充 cohort 沉淀的 app 留存事实表
- 目标粒度：`dt + app_code + channel + region + device`
- 核心指标：`first_recharge_users`、`day1_ret_cnt ~ day30_ret_cnt`
- 关键说明：
  - `dt` 表示**首充日期**，不是活跃日期
  - `first_recharge_users` 取 `dim.dim_user_all.first_recharge_time` 命中的首充 cohort
  - 留存活跃定义使用 `dwd.dwd_app_page_view_d` 中出现的 `uid`
  - 当前程序主来源不直接读取 `dwd.dwd_order_paid_d`，但核查时必须用 `dwd.dwd_order_paid_d` 的历史首次支付时间做首充本质交叉验证

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_code` / `app_id`、`channel`、`region`、`device`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该首充日全量 app 的全维度结果
  - 传 `dt + app_code/app_id`：核查指定 app
  - 其他维度参数仅用于下钻，不改变最终对账粒度规则

## 3. 绑定程序
- 绑定处理程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_user_first_recharge_retention_d/dws_user_first_recharge_retention_d.sql`
- 当前绑定说明：`/datacheck` 执行首充留存模型表核查时，默认以该 SQL 的已上线实现为程序参考。
- 关键逻辑块：
  - `app_page_view`：提取活跃行为，按 `dt + app_id + channel + uid` 取 `MAX(event_time)`
  - `first_recharge`：从 `dim.dim_user_all` 提取 `first_recharge_time`，并完成设备归一、地区映射
  - 最终 `GROUP BY`：按 `dt + app_id + channel + region + device` 聚合
- 已确认逻辑：
  - 首充 cohort 当前以 `dim.dim_user_all.first_recharge_time` 为准
  - 活跃定义：`dwd.dwd_app_page_view_d` 中的 `app_page_view`
  - 区域映射：`dim.dim_region_info_all`
  - 设备归一：`IOS / ANDROID / PC / OTHER`
  - 留存成熟规则：未到成熟日的 `dayN_ret_cnt` 应保持 `NULL`
  - 首充本质规则：需额外用 `dwd.dwd_order_paid_d` 对 `MIN(event_time)` 做交叉验证，确认 `dim.dim_user_all.first_recharge_time` 未偏离“生命周期首次充值”
- 业务/API 命名映射（与留存模型表一致）：
  - 次留 -> `day1_ret_cnt`
  - 3留 -> `day2_ret_cnt`
  - 7留 -> `day6_ret_cnt`
  - 15留 -> `day14_ret_cnt`
  - 30留 -> `day29_ret_cnt`
- 程序维护约定：若 `dim.dim_user_all.first_recharge_time` 生成逻辑、活跃定义、地区映射、设备归一或成熟日出值规则变化，必须同步更新本剧本与 `.claude/database/knowledge.md`。

## 4. 核查 parts

### part_01_basic_shape_and_sanity
- 目的：确认目标表基础形态、主键唯一性、空值、越界值与成熟日出值逻辑是否正常
- 来源表：`dws.dws_user_first_recharge_retention_d`
- 核查重点：
  - 指定日期是否有数据
  - 主键 `dt + app_code + channel + region + device` 是否唯一
  - 主键字段是否为空
  - `device` 是否仅出现 `IOS / ANDROID / PC / OTHER`
  - `first_recharge_users` 与各 `dayN_ret_cnt` 是否出现负值
  - 任意 `dayN_ret_cnt > first_recharge_users` 的异常
  - 未成熟日期是否被错误写成 0 或非空值
- 判定：任一关键字段为空、主键重复、负值、`ret_cnt > first_recharge_users` 或未成熟日期误出值，则该 part 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(first_recharge_users) AS total_first_recharge_users,
  SUM(day1_ret_cnt) AS total_day1_ret_cnt,
  SUM(day7_ret_cnt) AS total_day7_ret_cnt,
  SUM(day30_ret_cnt) AS total_day30_ret_cnt
FROM dws.dws_user_first_recharge_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}};
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
FROM dws.dws_user_first_recharge_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}}
GROUP BY dt, app_code, channel, region, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：空值、值域与越界检查
```sql
SELECT *
FROM dws.dws_user_first_recharge_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    app_code IS NULL
    OR channel IS NULL
    OR region IS NULL
    OR device IS NULL
    OR COALESCE(device, '__NULL__') NOT IN ('IOS', 'ANDROID', 'PC', 'OTHER')
    OR COALESCE(first_recharge_users, 0) < 0
    OR COALESCE(day1_ret_cnt, 0) < 0
    OR COALESCE(day2_ret_cnt, 0) < 0
    OR COALESCE(day3_ret_cnt, 0) < 0
    OR COALESCE(day4_ret_cnt, 0) < 0
    OR COALESCE(day5_ret_cnt, 0) < 0
    OR COALESCE(day6_ret_cnt, 0) < 0
    OR COALESCE(day7_ret_cnt, 0) < 0
    OR COALESCE(day8_ret_cnt, 0) < 0
    OR COALESCE(day9_ret_cnt, 0) < 0
    OR COALESCE(day10_ret_cnt, 0) < 0
    OR COALESCE(day11_ret_cnt, 0) < 0
    OR COALESCE(day12_ret_cnt, 0) < 0
    OR COALESCE(day13_ret_cnt, 0) < 0
    OR COALESCE(day14_ret_cnt, 0) < 0
    OR COALESCE(day15_ret_cnt, 0) < 0
    OR COALESCE(day16_ret_cnt, 0) < 0
    OR COALESCE(day17_ret_cnt, 0) < 0
    OR COALESCE(day18_ret_cnt, 0) < 0
    OR COALESCE(day19_ret_cnt, 0) < 0
    OR COALESCE(day20_ret_cnt, 0) < 0
    OR COALESCE(day21_ret_cnt, 0) < 0
    OR COALESCE(day22_ret_cnt, 0) < 0
    OR COALESCE(day23_ret_cnt, 0) < 0
    OR COALESCE(day24_ret_cnt, 0) < 0
    OR COALESCE(day25_ret_cnt, 0) < 0
    OR COALESCE(day26_ret_cnt, 0) < 0
    OR COALESCE(day27_ret_cnt, 0) < 0
    OR COALESCE(day28_ret_cnt, 0) < 0
    OR COALESCE(day29_ret_cnt, 0) < 0
    OR COALESCE(day30_ret_cnt, 0) < 0
    OR COALESCE(day1_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day2_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day3_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day4_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day5_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day6_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day7_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day8_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day9_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day10_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day11_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day12_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day13_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day14_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day15_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day16_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day17_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day18_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day19_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day20_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day21_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day22_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day23_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day24_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day25_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day26_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day27_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day28_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day29_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
    OR COALESCE(day30_ret_cnt, 0) > COALESCE(first_recharge_users, 0)
  )
LIMIT 100;
```

#### SQL：未成熟日期误出值检查
```sql
SELECT *
FROM dws.dws_user_first_recharge_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) AND day1_ret_cnt IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY) AND day2_ret_cnt IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) AND day3_ret_cnt IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND day7_ret_cnt IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) AND day15_ret_cnt IS NOT NULL)
    OR (dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) AND day30_ret_cnt IS NOT NULL)
  )
LIMIT 100;
```

### part_02_full_grain_source_reconciliation
- 目的：按真实处理逻辑做全维度来源重算与目标对账
- 来源表：`dim.dim_user_all`、`dwd.dwd_app_page_view_d`、`dim.dim_region_info_all`
- 最终对齐粒度：`dt + app_code + channel + region + device`
- 关键规则：
  - 最终正确性只能按全维度判断
  - 日级 `COUNT(DISTINCT uid)` 汇总只能作为诊断，不作为失败结论
  - 重复 uid 现象需要单列量化解释
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：全维度来源重算
```sql
WITH first_recharge_base AS (
  SELECT
    DATE(dua.first_recharge_time) AS dt,
    dua.app_id AS app_code,
    dua.channel,
    CASE WHEN UPPER(TRIM(dua.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(dua.device)) END AS device,
    COALESCE(d.region, 99999999) AS region,
    dua.uid,
    dua.first_recharge_time
  FROM dim.dim_user_all dua
  LEFT JOIN dim.dim_region_info_all d
    ON dua.country = d.country_name
   AND dua.province = d.province_name
   AND dua.city = d.city_name
  WHERE DATE(dua.first_recharge_time) = '{{dt}}'
    {{app_filter}}
    AND dua.uid IS NOT NULL
    AND TRIM(dua.uid) <> ''
),
app_page_view AS (
  SELECT
    dt,
    app_id,
    channel,
    uid,
    MAX(event_time) AS last_login_time
  FROM dwd.dwd_app_page_view_d
  WHERE dt BETWEEN '{{dt}}' AND DATE_ADD('{{dt}}', INTERVAL 30 DAY)
    AND uid IS NOT NULL
    AND TRIM(uid) <> ''
    {{app_filter}}
  GROUP BY dt, app_id, channel, uid
)
SELECT
  fr.dt,
  fr.app_code,
  fr.channel,
  fr.region,
  fr.device,
  COUNT(DISTINCT fr.uid) AS src_first_recharge_users,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 1 DAY), apv.uid, NULL)) ELSE NULL END AS src_day1_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 2 DAY), apv.uid, NULL)) ELSE NULL END AS src_day2_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 3 DAY), apv.uid, NULL)) ELSE NULL END AS src_day3_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 4 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 4 DAY), apv.uid, NULL)) ELSE NULL END AS src_day4_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 5 DAY), apv.uid, NULL)) ELSE NULL END AS src_day5_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 6 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 6 DAY), apv.uid, NULL)) ELSE NULL END AS src_day6_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 7 DAY), apv.uid, NULL)) ELSE NULL END AS src_day7_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 8 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 8 DAY), apv.uid, NULL)) ELSE NULL END AS src_day8_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 9 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 9 DAY), apv.uid, NULL)) ELSE NULL END AS src_day9_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 10 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 10 DAY), apv.uid, NULL)) ELSE NULL END AS src_day10_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 11 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 11 DAY), apv.uid, NULL)) ELSE NULL END AS src_day11_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 12 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 12 DAY), apv.uid, NULL)) ELSE NULL END AS src_day12_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 13 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 13 DAY), apv.uid, NULL)) ELSE NULL END AS src_day13_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 14 DAY), apv.uid, NULL)) ELSE NULL END AS src_day14_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 15 DAY), apv.uid, NULL)) ELSE NULL END AS src_day15_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 16 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 16 DAY), apv.uid, NULL)) ELSE NULL END AS src_day16_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 17 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 17 DAY), apv.uid, NULL)) ELSE NULL END AS src_day17_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 18 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 18 DAY), apv.uid, NULL)) ELSE NULL END AS src_day18_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 19 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 19 DAY), apv.uid, NULL)) ELSE NULL END AS src_day19_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 20 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 20 DAY), apv.uid, NULL)) ELSE NULL END AS src_day20_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 21 DAY), apv.uid, NULL)) ELSE NULL END AS src_day21_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 22 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 22 DAY), apv.uid, NULL)) ELSE NULL END AS src_day22_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 23 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 23 DAY), apv.uid, NULL)) ELSE NULL END AS src_day23_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 24 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 24 DAY), apv.uid, NULL)) ELSE NULL END AS src_day24_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 25 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 25 DAY), apv.uid, NULL)) ELSE NULL END AS src_day25_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 26 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 26 DAY), apv.uid, NULL)) ELSE NULL END AS src_day26_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 27 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 27 DAY), apv.uid, NULL)) ELSE NULL END AS src_day27_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 28 DAY), apv.uid, NULL)) ELSE NULL END AS src_day28_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 29 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 29 DAY), apv.uid, NULL)) ELSE NULL END AS src_day29_ret_cnt,
  CASE WHEN fr.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(fr.dt, INTERVAL 30 DAY), apv.uid, NULL)) ELSE NULL END AS src_day30_ret_cnt
FROM first_recharge_base fr
LEFT JOIN app_page_view apv
  ON apv.app_id = fr.app_code
 AND apv.channel = fr.channel
 AND apv.uid = fr.uid
GROUP BY fr.dt, fr.app_code, fr.channel, fr.region, fr.device;
```

#### SQL：全维度来源对账异常明细
```sql
WITH src AS (
  -- 将上一段“全维度来源重算”SQL 放在这里
),
tgt AS (
  SELECT *
  FROM dws.dws_user_first_recharge_retention_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
)
SELECT
  COALESCE(tgt.dt, src.dt) AS dt,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  tgt.first_recharge_users, src.src_first_recharge_users,
  tgt.day1_ret_cnt, src.src_day1_ret_cnt,
  tgt.day2_ret_cnt, src.src_day2_ret_cnt,
  tgt.day3_ret_cnt, src.src_day3_ret_cnt,
  tgt.day7_ret_cnt, src.src_day7_ret_cnt,
  tgt.day15_ret_cnt, src.src_day15_ret_cnt,
  tgt.day30_ret_cnt, src.src_day30_ret_cnt
FROM tgt
FULL OUTER JOIN src
  ON tgt.dt = src.dt
 AND tgt.app_code = src.app_code
 AND tgt.channel = src.channel
 AND tgt.region = src.region
 AND tgt.device = src.device
WHERE
  COALESCE(tgt.first_recharge_users, -1) <> COALESCE(src.src_first_recharge_users, -1)
  OR COALESCE(tgt.day1_ret_cnt, -1) <> COALESCE(src.src_day1_ret_cnt, -1)
  OR COALESCE(tgt.day2_ret_cnt, -1) <> COALESCE(src.src_day2_ret_cnt, -1)
  OR COALESCE(tgt.day3_ret_cnt, -1) <> COALESCE(src.src_day3_ret_cnt, -1)
  OR COALESCE(tgt.day4_ret_cnt, -1) <> COALESCE(src.src_day4_ret_cnt, -1)
  OR COALESCE(tgt.day5_ret_cnt, -1) <> COALESCE(src.src_day5_ret_cnt, -1)
  OR COALESCE(tgt.day6_ret_cnt, -1) <> COALESCE(src.src_day6_ret_cnt, -1)
  OR COALESCE(tgt.day7_ret_cnt, -1) <> COALESCE(src.src_day7_ret_cnt, -1)
  OR COALESCE(tgt.day8_ret_cnt, -1) <> COALESCE(src.src_day8_ret_cnt, -1)
  OR COALESCE(tgt.day9_ret_cnt, -1) <> COALESCE(src.src_day9_ret_cnt, -1)
  OR COALESCE(tgt.day10_ret_cnt, -1) <> COALESCE(src.src_day10_ret_cnt, -1)
  OR COALESCE(tgt.day11_ret_cnt, -1) <> COALESCE(src.src_day11_ret_cnt, -1)
  OR COALESCE(tgt.day12_ret_cnt, -1) <> COALESCE(src.src_day12_ret_cnt, -1)
  OR COALESCE(tgt.day13_ret_cnt, -1) <> COALESCE(src.src_day13_ret_cnt, -1)
  OR COALESCE(tgt.day14_ret_cnt, -1) <> COALESCE(src.src_day14_ret_cnt, -1)
  OR COALESCE(tgt.day15_ret_cnt, -1) <> COALESCE(src.src_day15_ret_cnt, -1)
  OR COALESCE(tgt.day16_ret_cnt, -1) <> COALESCE(src.src_day16_ret_cnt, -1)
  OR COALESCE(tgt.day17_ret_cnt, -1) <> COALESCE(src.src_day17_ret_cnt, -1)
  OR COALESCE(tgt.day18_ret_cnt, -1) <> COALESCE(src.src_day18_ret_cnt, -1)
  OR COALESCE(tgt.day19_ret_cnt, -1) <> COALESCE(src.src_day19_ret_cnt, -1)
  OR COALESCE(tgt.day20_ret_cnt, -1) <> COALESCE(src.src_day20_ret_cnt, -1)
  OR COALESCE(tgt.day21_ret_cnt, -1) <> COALESCE(src.src_day21_ret_cnt, -1)
  OR COALESCE(tgt.day22_ret_cnt, -1) <> COALESCE(src.src_day22_ret_cnt, -1)
  OR COALESCE(tgt.day23_ret_cnt, -1) <> COALESCE(src.src_day23_ret_cnt, -1)
  OR COALESCE(tgt.day24_ret_cnt, -1) <> COALESCE(src.src_day24_ret_cnt, -1)
  OR COALESCE(tgt.day25_ret_cnt, -1) <> COALESCE(src.src_day25_ret_cnt, -1)
  OR COALESCE(tgt.day26_ret_cnt, -1) <> COALESCE(src.src_day26_ret_cnt, -1)
  OR COALESCE(tgt.day27_ret_cnt, -1) <> COALESCE(src.src_day27_ret_cnt, -1)
  OR COALESCE(tgt.day28_ret_cnt, -1) <> COALESCE(src.src_day28_ret_cnt, -1)
  OR COALESCE(tgt.day29_ret_cnt, -1) <> COALESCE(src.src_day29_ret_cnt, -1)
  OR COALESCE(tgt.day30_ret_cnt, -1) <> COALESCE(src.src_day30_ret_cnt, -1)
LIMIT 100;
```

### part_03_first_recharge_direct_rule_cross_check
- 目的：验证 `dim.dim_user_all.first_recharge_time` 是否与“生命周期首次充值”本质规则一致
- 来源表：`dim.dim_user_all`、`dwd.dwd_order_paid_d`
- 关键规则：
  - 用户首充定义必须等于 `dwd.dwd_order_paid_d` 中 `MIN(event_time)`
  - 匹配键使用 `app_id + channel + uid`
- 判定：若 `dim_only_users > 0` 或 `direct_only_users > 0`，则该 part 失败

#### SQL：首充 cohort 一致性汇总
```sql
WITH dim_cohort AS (
  SELECT
    DATE(first_recharge_time) AS dt,
    app_id,
    channel,
    uid
  FROM dim.dim_user_all
  WHERE DATE(first_recharge_time) = '{{dt}}'
    {{app_filter}}
    AND uid IS NOT NULL
    AND TRIM(uid) <> ''
),
direct_cohort AS (
  SELECT
    DATE(MIN(event_time)) AS dt,
    app_id,
    channel,
    uid,
    MIN(event_time) AS first_paid_time
  FROM dwd.dwd_order_paid_d
  WHERE dt <= '{{dt}}'
    {{app_filter}}
    AND app_id IS NOT NULL
    AND uid IS NOT NULL
  GROUP BY app_id, channel, uid
  HAVING DATE(MIN(event_time)) = '{{dt}}'
)
SELECT
  SUM(CASE WHEN d.uid IS NOT NULL AND h.uid IS NOT NULL THEN 1 ELSE 0 END) AS matched_users,
  SUM(CASE WHEN d.uid IS NOT NULL AND h.uid IS NULL THEN 1 ELSE 0 END) AS dim_only_users,
  SUM(CASE WHEN d.uid IS NULL AND h.uid IS NOT NULL THEN 1 ELSE 0 END) AS direct_only_users
FROM dim_cohort d
FULL OUTER JOIN direct_cohort h
  ON d.dt = h.dt
 AND d.app_id = h.app_id
 AND d.channel = h.channel
 AND d.uid = h.uid;
```

#### SQL：首充 cohort 差异样本
```sql
WITH dim_cohort AS (
  SELECT
    DATE(first_recharge_time) AS dt,
    app_id,
    channel,
    uid,
    first_recharge_time
  FROM dim.dim_user_all
  WHERE DATE(first_recharge_time) = '{{dt}}'
    {{app_filter}}
    AND uid IS NOT NULL
    AND TRIM(uid) <> ''
),
direct_cohort AS (
  SELECT
    DATE(MIN(event_time)) AS dt,
    app_id,
    channel,
    uid,
    MIN(event_time) AS first_paid_time
  FROM dwd.dwd_order_paid_d
  WHERE dt <= '{{dt}}'
    {{app_filter}}
    AND app_id IS NOT NULL
    AND uid IS NOT NULL
  GROUP BY app_id, channel, uid
  HAVING DATE(MIN(event_time)) = '{{dt}}'
)
SELECT
  COALESCE(d.dt, h.dt) AS dt,
  COALESCE(d.app_id, h.app_id) AS app_id,
  COALESCE(d.channel, h.channel) AS channel,
  COALESCE(d.uid, h.uid) AS uid,
  d.first_recharge_time AS dim_first_recharge_time,
  h.first_paid_time AS direct_first_paid_time,
  CASE
    WHEN d.uid IS NOT NULL AND h.uid IS NULL THEN 'dim_only'
    WHEN d.uid IS NULL AND h.uid IS NOT NULL THEN 'direct_only'
    ELSE 'matched'
  END AS diff_type
FROM dim_cohort d
FULL OUTER JOIN direct_cohort h
  ON d.dt = h.dt
 AND d.app_id = h.app_id
 AND d.channel = h.channel
 AND d.uid = h.uid
WHERE d.uid IS NULL OR h.uid IS NULL
LIMIT 100;
```

### part_04_duplicate_uid_quantification
- 目的：量化同一首充日跨多个维度行出现的重复 uid 规模，解释日级 `COUNT(DISTINCT uid)` 与目标表汇总差异来源
- 来源表：`dim.dim_user_all`、`dim.dim_region_info_all`
- 关键规则：
  - 重复 uid 现象本身不是失败结论
  - 只有全维度来源对账不一致才算失败

#### SQL：重复 uid 规模汇总
```sql
WITH first_recharge_base AS (
  SELECT
    DATE(dua.first_recharge_time) AS dt,
    dua.app_id AS app_code,
    dua.channel,
    CASE WHEN UPPER(TRIM(dua.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(dua.device)) END AS device,
    COALESCE(d.region, 99999999) AS region,
    dua.uid
  FROM dim.dim_user_all dua
  LEFT JOIN dim.dim_region_info_all d
    ON dua.country = d.country_name
   AND dua.province = d.province_name
   AND dua.city = d.city_name
  WHERE DATE(dua.first_recharge_time) = '{{dt}}'
    {{app_filter}}
    AND dua.uid IS NOT NULL
    AND TRIM(dua.uid) <> ''
),
uid_scope AS (
  SELECT
    dt,
    uid,
    COUNT(DISTINCT CONCAT_WS('|', app_code, channel, region, device)) AS grain_cnt
  FROM first_recharge_base
  GROUP BY dt, uid
)
SELECT
  COUNT(*) AS distinct_uid_cnt,
  SUM(CASE WHEN grain_cnt > 1 THEN 1 ELSE 0 END) AS duplicated_uid_cnt,
  SUM(grain_cnt) AS summed_grain_cnt,
  SUM(grain_cnt) - COUNT(*) AS extra_grain_rows
FROM uid_scope;
```

#### SQL：重复 uid 样本
```sql
WITH first_recharge_base AS (
  SELECT
    DATE(dua.first_recharge_time) AS dt,
    dua.app_id AS app_code,
    dua.channel,
    CASE WHEN UPPER(TRIM(dua.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(dua.device)) END AS device,
    COALESCE(d.region, 99999999) AS region,
    dua.uid
  FROM dim.dim_user_all dua
  LEFT JOIN dim.dim_region_info_all d
    ON dua.country = d.country_name
   AND dua.province = d.province_name
   AND dua.city = d.city_name
  WHERE DATE(dua.first_recharge_time) = '{{dt}}'
    {{app_filter}}
    AND dua.uid IS NOT NULL
    AND TRIM(dua.uid) <> ''
),
uid_scope AS (
  SELECT dt, uid
  FROM first_recharge_base
  GROUP BY dt, uid
  HAVING COUNT(DISTINCT CONCAT_WS('|', app_code, channel, region, device)) > 1
)
SELECT b.*
FROM first_recharge_base b
INNER JOIN uid_scope s
  ON b.dt = s.dt
 AND b.uid = s.uid
ORDER BY b.uid, b.app_code, b.channel, b.region, b.device
LIMIT 100;
```

### part_05_retention_curve_anomaly_check
- 目的：从业务视角识别首充留存曲线反弹、突增、晚期 spike 等异常走势
- 来源表：`dws.dws_user_first_recharge_retention_d`
- 关键规则：
  - 这是业务异常核查，不等同于来源对账失败
  - 需要把“来源对账异常”和“曲线异常”分开表述

#### SQL：按 app + dt 聚合后的曲线检查
```sql
WITH agg AS (
  SELECT
    dt,
    app_code,
    SUM(first_recharge_users) AS first_recharge_users,
    SUM(day1_ret_cnt) AS day1_ret_cnt,
    SUM(day2_ret_cnt) AS day2_ret_cnt,
    SUM(day6_ret_cnt) AS day6_ret_cnt,
    SUM(day14_ret_cnt) AS day14_ret_cnt,
    SUM(day29_ret_cnt) AS day29_ret_cnt
  FROM dws.dws_user_first_recharge_retention_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 6 DAY) AND '{{dt}}'
    {{app_filter}}
  GROUP BY dt, app_code
)
SELECT
  dt,
  app_code,
  first_recharge_users,
  day1_ret_cnt,
  ROUND(day1_ret_cnt / NULLIF(first_recharge_users, 0), 4) AS day1_rate,
  day2_ret_cnt,
  ROUND(day2_ret_cnt / NULLIF(first_recharge_users, 0), 4) AS day3_rate,
  day6_ret_cnt,
  ROUND(day6_ret_cnt / NULLIF(first_recharge_users, 0), 4) AS day7_rate,
  day14_ret_cnt,
  ROUND(day14_ret_cnt / NULLIF(first_recharge_users, 0), 4) AS day15_rate,
  day29_ret_cnt,
  ROUND(day29_ret_cnt / NULLIF(first_recharge_users, 0), 4) AS day30_rate
FROM agg
ORDER BY dt, app_code;
```

## 5. 输出建议
- 优先输出：核查范围、关键 SQL 逻辑、结果表格、异常定位、结论
- 若发现 mismatch：
  1. 先给全维度对账结论
  2. 再单列 `dim.first_recharge_time` 与 `dwd.dwd_order_paid_d` 历史首次支付是否一致
  3. 如有日级汇总差异，必须说明是否由重复 uid 引起
- 若需要落地报告，默认写到 `.claude/database/reports/`
