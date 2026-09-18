# dws.dws_app_retention_d 核查剧本

## 1. 表信息
- 表名：`dws.dws_app_retention_d`
- 业务名：留存模型表
- 状态：上线
- 表说明：按注册 cohort 沉淀的 app 留存事实表
- 目标粒度：`dt + app_code + channel + region + device`
- 关键说明：`dt` 表示注册日期，不是活跃日期

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_code` / `app_id`、`channel`、`region`、`device`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该日期全量 app 的全维度结果
  - 传 `dt + app_code/app_id`：核查指定 app
  - 其他维度参数仅用于下钻，不改变最终对账粒度规则

## 3. 绑定程序
- 绑定处理程序：`/Users/arthur/Program/datacenter/dc-parent/operating-system/06.分析模型/维度表/dws_app_retention_d.sql`
- 当前绑定说明：`/datacheck` 执行留存模型表核查时，默认以该 SQL 的已上线实现为程序参考，不需要额外打开程序。
- 关键逻辑块：
  - `user_register`：注册 cohort 提取与首条注册去重
  - `app_page_view`：活跃行为提取
  - 最终 `GROUP BY`：按 `dt + app_id + channel + region + device` 聚合
- 已确认逻辑：
  - 注册去重规则：`ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time)`
  - 活跃定义：`dwd.dwd_app_page_view_d` 中的 `app_page_view`
  - 区域映射：`dim.dim_region_info_all`
  - 设备归一：`IOS / ANDROID / PC / OTHER`
  - 留存成熟规则：未到成熟日的 `dayN_ret_cnt` 应保持 `NULL`
- 业务/API 命名映射：
  - 次留 -> `day1_ret_cnt`
  - 3留 -> `day2_ret_cnt`
  - 7留 -> `day6_ret_cnt`
  - 15留 -> `day14_ret_cnt`
  - 30留 -> `day29_ret_cnt`
- 程序维护约定：若注册去重、地区映射、设备归一、活跃事件来源、成熟日出值规则或业务/API 留存列映射变化，必须同步更新本剧本与 `.claude/database/knowledge.md`。

## 4. 核查 parts

### part_01_basic_shape_and_sanity
- 目的：确认目标表基础形态、空值、越界值与成熟日出值逻辑是否正常
- 来源表：`dws.dws_app_retention_d`
- 核查重点：
  - 指定日期是否有数据
  - 主键字段是否为空
  - `new_users` 与 `day1~day30` 是否出现负值
  - 任意 `dayN_ret_cnt > new_users` 的异常
  - 未成熟日期是否被错误写成 0 或非空值
- 判定：
  - 任一关键字段为空、负值、`ret_cnt > new_users` 或未成熟日期误出值，则该 part 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(new_users) AS total_new_users
FROM dws.dws_app_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}};
```

#### SQL：关键字段空值检查
```sql
SELECT *
FROM dws.dws_app_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    app_code IS NULL
    OR channel IS NULL
    OR region IS NULL
    OR device IS NULL
  )
LIMIT 100;
```

#### SQL：负值与留存人数越界检查
```sql
SELECT *
FROM dws.dws_app_retention_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  AND (
    COALESCE(new_users, 0) < 0
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
    OR COALESCE(day1_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day2_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day3_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day4_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day5_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day6_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day7_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day8_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day9_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day10_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day11_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day12_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day13_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day14_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day15_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day16_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day17_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day18_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day19_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day20_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day21_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day22_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day23_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day24_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day25_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day26_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day27_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day28_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day29_ret_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(day30_ret_cnt, 0) > COALESCE(new_users, 0)
  )
LIMIT 100;
```

#### SQL：未成熟日期误出值检查
```sql
SELECT *
FROM dws.dws_app_retention_d
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
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_app_page_view_d`、`dim.dim_region_info_all`
- 最终对齐粒度：`dt + app_code + channel + region + device`
- 关键规则：
  - 最终正确性只能按全维度判断
  - `dt + app_code` 或 `dt + app_code + channel` 的汇总 mismatch 只能作为诊断，不作为失败结论
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：全维度来源重算
```sql
WITH user_register AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    t1.uid,
    t1.event_time AS register_time,
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
  ur.dt,
  ur.app_code,
  ur.channel,
  ur.region,
  ur.device,
  COUNT(DISTINCT ur.uid) AS src_new_users,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 1 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day1_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 2 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 2 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day2_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 3 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day3_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 4 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 4 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day4_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 5 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 5 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day5_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 6 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 6 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day6_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 7 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day7_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 8 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 8 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day8_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 9 DAY)  THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 9 DAY),  apv.uid, NULL)) ELSE NULL END AS src_day9_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 10 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 10 DAY), apv.uid, NULL)) ELSE NULL END AS src_day10_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 11 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 11 DAY), apv.uid, NULL)) ELSE NULL END AS src_day11_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 12 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 12 DAY), apv.uid, NULL)) ELSE NULL END AS src_day12_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 13 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 13 DAY), apv.uid, NULL)) ELSE NULL END AS src_day13_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 14 DAY), apv.uid, NULL)) ELSE NULL END AS src_day14_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 15 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 15 DAY), apv.uid, NULL)) ELSE NULL END AS src_day15_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 16 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 16 DAY), apv.uid, NULL)) ELSE NULL END AS src_day16_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 17 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 17 DAY), apv.uid, NULL)) ELSE NULL END AS src_day17_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 18 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 18 DAY), apv.uid, NULL)) ELSE NULL END AS src_day18_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 19 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 19 DAY), apv.uid, NULL)) ELSE NULL END AS src_day19_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 20 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 20 DAY), apv.uid, NULL)) ELSE NULL END AS src_day20_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 21 DAY), apv.uid, NULL)) ELSE NULL END AS src_day21_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 22 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 22 DAY), apv.uid, NULL)) ELSE NULL END AS src_day22_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 23 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 23 DAY), apv.uid, NULL)) ELSE NULL END AS src_day23_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 24 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 24 DAY), apv.uid, NULL)) ELSE NULL END AS src_day24_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 25 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 25 DAY), apv.uid, NULL)) ELSE NULL END AS src_day25_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 26 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 26 DAY), apv.uid, NULL)) ELSE NULL END AS src_day26_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 27 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 27 DAY), apv.uid, NULL)) ELSE NULL END AS src_day27_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 28 DAY), apv.uid, NULL)) ELSE NULL END AS src_day28_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 29 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 29 DAY), apv.uid, NULL)) ELSE NULL END AS src_day29_ret_cnt,
  CASE WHEN ur.dt < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) THEN COUNT(DISTINCT IF(DATE(apv.last_login_time) = DATE_ADD(DATE(ur.register_time), INTERVAL 30 DAY), apv.uid, NULL)) ELSE NULL END AS src_day30_ret_cnt
FROM user_register ur
LEFT JOIN app_page_view apv
  ON apv.app_id = ur.app_code
 AND apv.channel = ur.channel
 AND apv.uid = ur.uid
GROUP BY ur.dt, ur.app_code, ur.channel, ur.region, ur.device;
```

#### SQL：全维度来源对账异常明细
```sql
WITH src AS (
  -- 将上一段“全维度来源重算”SQL 放在这里
),
tgt AS (
  SELECT *
  FROM dws.dws_app_retention_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
)
SELECT
  COALESCE(tgt.dt, src.dt) AS dt,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  tgt.new_users, src.src_new_users,
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
  COALESCE(tgt.new_users, -1) <> COALESCE(src.src_new_users, -1)
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

### part_03_duplicate_uid_quantification
- 目的：量化跨 region / 跨 device 的重复 uid 规模，解释 app 汇总口径偏差来源
- 来源表：`dwd.dwd_user_register_d_v2`、`dim.dim_region_info_all`
- 关键规则：
  - 重复 uid 需要单独报告
  - 重复 uid 现象本身不是失败结论，只有全维度来源对账不一致才算失败

#### SQL：重复 uid 规模汇总
```sql
WITH user_register AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    t1.uid,
    COALESCE(d.region, 99999999) AS region
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid, country, province, city, device, channel ORDER BY event_time) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
      AND uid IS NOT NULL
      AND TRIM(uid) <> ''
  ) t1
  LEFT JOIN dim.dim_region_info_all d
    ON t1.country = d.country_name
   AND t1.province = d.province_name
   AND t1.city = d.city_name
  WHERE t1.rn = 1
),
uid_scope AS (
  SELECT
    dt,
    app_code,
    channel,
    uid,
    COUNT(DISTINCT region) AS region_cnt,
    COUNT(DISTINCT device) AS device_cnt,
    COUNT(*) AS row_cnt
  FROM user_register
  GROUP BY dt, app_code, channel, uid
)
SELECT
  COUNT(*) AS uid_scope_cnt,
  SUM(CASE WHEN region_cnt > 1 THEN 1 ELSE 0 END) AS cross_region_uid_cnt,
  SUM(CASE WHEN device_cnt > 1 THEN 1 ELSE 0 END) AS cross_device_uid_cnt,
  SUM(CASE WHEN region_cnt > 1 OR device_cnt > 1 THEN 1 ELSE 0 END) AS duplicated_uid_cnt,
  SUM(CASE WHEN region_cnt > 1 OR device_cnt > 1 THEN row_cnt ELSE 0 END) AS duplicated_uid_rows
FROM uid_scope;
```

#### SQL：重复 uid 样本
```sql
WITH user_register AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    t1.channel,
    CASE WHEN UPPER(TRIM(t1.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER' ELSE UPPER(TRIM(t1.device)) END AS device,
    t1.uid,
    COALESCE(d.region, 99999999) AS region,
    t1.country,
    t1.province,
    t1.city
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid, country, province, city, device, channel ORDER BY event_time) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
      AND uid IS NOT NULL
      AND TRIM(uid) <> ''
  ) t1
  LEFT JOIN dim.dim_region_info_all d
    ON t1.country = d.country_name
   AND t1.province = d.province_name
   AND t1.city = d.city_name
  WHERE t1.rn = 1
),
uid_scope AS (
  SELECT dt, app_code, channel, uid
  FROM user_register
  GROUP BY dt, app_code, channel, uid
  HAVING COUNT(DISTINCT region) > 1 OR COUNT(DISTINCT device) > 1
)
SELECT ur.*
FROM user_register ur
INNER JOIN uid_scope s
  ON ur.dt = s.dt
 AND ur.app_code = s.app_code
 AND ur.channel = s.channel
 AND ur.uid = s.uid
ORDER BY ur.app_code, ur.channel, ur.uid
LIMIT 100;
```

### part_04_retention_curve_anomaly_check
- 目的：从业务视角识别留存曲线反弹、突增、晚期 spike 等异常走势
- 来源表：`dws.dws_app_retention_d`
- 关键规则：
  - 这是业务异常核查，不等同于来源对账失败
  - 需要把“来源对账异常”和“曲线异常”分开表述

#### SQL：按 app + dt 聚合后的曲线检查
```sql
WITH agg AS (
  SELECT
    dt,
    app_code,
    SUM(new_users) AS new_users,
    SUM(day1_ret_cnt) AS day1_ret_cnt,
    SUM(day2_ret_cnt) AS day2_ret_cnt,
    SUM(day3_ret_cnt) AS day3_ret_cnt,
    SUM(day4_ret_cnt) AS day4_ret_cnt,
    SUM(day5_ret_cnt) AS day5_ret_cnt,
    SUM(day6_ret_cnt) AS day6_ret_cnt,
    SUM(day7_ret_cnt) AS day7_ret_cnt,
    SUM(day8_ret_cnt) AS day8_ret_cnt,
    SUM(day9_ret_cnt) AS day9_ret_cnt,
    SUM(day10_ret_cnt) AS day10_ret_cnt,
    SUM(day11_ret_cnt) AS day11_ret_cnt,
    SUM(day12_ret_cnt) AS day12_ret_cnt,
    SUM(day13_ret_cnt) AS day13_ret_cnt,
    SUM(day14_ret_cnt) AS day14_ret_cnt,
    SUM(day15_ret_cnt) AS day15_ret_cnt,
    SUM(day16_ret_cnt) AS day16_ret_cnt,
    SUM(day17_ret_cnt) AS day17_ret_cnt,
    SUM(day18_ret_cnt) AS day18_ret_cnt,
    SUM(day19_ret_cnt) AS day19_ret_cnt,
    SUM(day20_ret_cnt) AS day20_ret_cnt,
    SUM(day21_ret_cnt) AS day21_ret_cnt,
    SUM(day22_ret_cnt) AS day22_ret_cnt,
    SUM(day23_ret_cnt) AS day23_ret_cnt,
    SUM(day24_ret_cnt) AS day24_ret_cnt,
    SUM(day25_ret_cnt) AS day25_ret_cnt,
    SUM(day26_ret_cnt) AS day26_ret_cnt,
    SUM(day27_ret_cnt) AS day27_ret_cnt,
    SUM(day28_ret_cnt) AS day28_ret_cnt,
    SUM(day29_ret_cnt) AS day29_ret_cnt,
    SUM(day30_ret_cnt) AS day30_ret_cnt
  FROM dws.dws_app_retention_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 6 DAY) AND '{{dt}}'
    {{app_filter}}
  GROUP BY dt, app_code
)
SELECT
  dt,
  app_code,
  new_users,
  day1_ret_cnt, day2_ret_cnt, day3_ret_cnt, day4_ret_cnt, day5_ret_cnt,
  day6_ret_cnt, day7_ret_cnt, day14_ret_cnt, day29_ret_cnt,
  (CASE WHEN day2_ret_cnt  > day1_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day3_ret_cnt  > day2_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day4_ret_cnt  > day3_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day5_ret_cnt  > day4_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day6_ret_cnt  > day5_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day7_ret_cnt  > day6_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day8_ret_cnt  > day7_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day9_ret_cnt  > day8_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day10_ret_cnt > day9_ret_cnt  THEN 1 ELSE 0 END
   + CASE WHEN day11_ret_cnt > day10_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day12_ret_cnt > day11_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day13_ret_cnt > day12_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day14_ret_cnt > day13_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day15_ret_cnt > day14_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day16_ret_cnt > day15_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day17_ret_cnt > day16_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day18_ret_cnt > day17_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day19_ret_cnt > day18_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day20_ret_cnt > day19_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day21_ret_cnt > day20_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day22_ret_cnt > day21_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day23_ret_cnt > day22_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day24_ret_cnt > day23_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day25_ret_cnt > day24_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day26_ret_cnt > day25_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day27_ret_cnt > day26_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day28_ret_cnt > day27_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day29_ret_cnt > day28_ret_cnt THEN 1 ELSE 0 END
   + CASE WHEN day30_ret_cnt > day29_ret_cnt THEN 1 ELSE 0 END) AS rebound_points
FROM agg
WHERE (
   day2_ret_cnt  > day1_ret_cnt OR day3_ret_cnt  > day2_ret_cnt OR day4_ret_cnt  > day3_ret_cnt OR
   day5_ret_cnt  > day4_ret_cnt OR day6_ret_cnt  > day5_ret_cnt OR day7_ret_cnt  > day6_ret_cnt OR
   day8_ret_cnt  > day7_ret_cnt OR day9_ret_cnt  > day8_ret_cnt OR day10_ret_cnt > day9_ret_cnt OR
   day11_ret_cnt > day10_ret_cnt OR day12_ret_cnt > day11_ret_cnt OR day13_ret_cnt > day12_ret_cnt OR
   day14_ret_cnt > day13_ret_cnt OR day15_ret_cnt > day14_ret_cnt OR day16_ret_cnt > day15_ret_cnt OR
   day17_ret_cnt > day16_ret_cnt OR day18_ret_cnt > day17_ret_cnt OR day19_ret_cnt > day18_ret_cnt OR
   day20_ret_cnt > day19_ret_cnt OR day21_ret_cnt > day20_ret_cnt OR day22_ret_cnt > day21_ret_cnt OR
   day23_ret_cnt > day22_ret_cnt OR day24_ret_cnt > day23_ret_cnt OR day25_ret_cnt > day24_ret_cnt OR
   day26_ret_cnt > day25_ret_cnt OR day27_ret_cnt > day26_ret_cnt OR day28_ret_cnt > day27_ret_cnt OR
   day29_ret_cnt > day28_ret_cnt OR day30_ret_cnt > day29_ret_cnt
)
ORDER BY rebound_points DESC, new_users DESC
LIMIT 100;
```

#### SQL：晚期 spike 样本
```sql
WITH agg AS (
  SELECT
    dt,
    app_code,
    SUM(new_users) AS new_users,
    SUM(day6_ret_cnt) AS day6_ret_cnt,
    SUM(day7_ret_cnt) AS day7_ret_cnt,
    SUM(day14_ret_cnt) AS day14_ret_cnt,
    SUM(day15_ret_cnt) AS day15_ret_cnt,
    SUM(day29_ret_cnt) AS day29_ret_cnt,
    SUM(day30_ret_cnt) AS day30_ret_cnt
  FROM dws.dws_app_retention_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 30 DAY) AND '{{dt}}'
    {{app_filter}}
  GROUP BY dt, app_code
)
SELECT *
FROM agg
WHERE (
    (COALESCE(day7_ret_cnt,0)  > COALESCE(day6_ret_cnt,0)  AND COALESCE(day6_ret_cnt,0)  = 0)
 OR (COALESCE(day15_ret_cnt,0) > COALESCE(day14_ret_cnt,0) AND COALESCE(day14_ret_cnt,0) = 0)
 OR (COALESCE(day30_ret_cnt,0) > COALESCE(day29_ret_cnt,0) AND COALESCE(day29_ret_cnt,0) = 0)
)
ORDER BY new_users DESC
LIMIT 100;
```

### part_05_exception_sampling_and_alias_note
- 目的：统一输出异常样本，并显式说明业务/API 与物理列映射
- 必含内容：
  - 全维度来源不一致样本（如存在）
  - 重复 uid 样本
  - 曲线异常样本
  - 映射说明：次留=`day1_ret_cnt`，3留=`day2_ret_cnt`，7留=`day6_ret_cnt`，15留=`day14_ret_cnt`，30留=`day29_ret_cnt`
- 判定：该 part 为说明性输出，不单独判失败；其结论依赖前述 parts

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_app_retention_d/`
- 建议文件名：
  - 无 app 过滤：`validate__{{dt}}__{{timestamp}}.md`
  - 有 app 过滤：`validate__{{dt}}__app_{{app_code}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：明确“全维度来源核对是否通过”
  2. 核查大类汇总：基础形态、来源对账、重复 uid、曲线异常、异常样本
  3. 逐条规则结果：每条规则要给出核验范围、异常量/样本量、结论
  4. 问题与处理建议：区分来源错误、解释性重复现象、业务曲线异常
  5. 映射说明：明确业务/API 留存名与物理列的对应关系
- 报告中的所有结论都应带数据，不能只写口头判断。

## 6. 剧本维护约定
- 该剧本默认绑定 `/Users/arthur/Program/datacenter/dc-parent/operating-system/06.分析模型/维度表/dws_app_retention_d.sql`。
- 若注册首条事件去重、区域映射、设备归一、活跃定义、成熟日出值规则、留存物理列或业务/API 留存映射发生变化，必须同步更新本剧本。
- 若后续发现 app 汇总层的诊断口径需要单独保留，也必须显式标注为“诊断视角”，不能覆盖全维度来源核对结论。
