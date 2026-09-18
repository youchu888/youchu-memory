# dws.dws_app_user_dwm 联动核查剧本

## 1. 表信息
- 目标表：`dws.dws_app_user_d`、`dws.dws_app_user_w`、`dws.dws_app_user_m`
- 业务名：用户模型天 / 周 / 月联动核查
- 状态：上线
- 表说明：统一校验用户模型日表、周表、月表的结构、来源口径、周期边界与跨周期一致性
- 目标粒度：
  - 日表：`dt + app_code + channel + region + device`
  - 周表：`week + app_code + channel + region + device`
  - 月表：`month + app_code + channel + region + device`
- 关键说明：
  - 三张表 SQL 实际都按 `user_type` 出数，但当前物理主键均未包含 `user_type`
  - 周表当前仍使用 `COUNT(DISTINCT ...)` 精确去重
  - 月表当前对 `new_users`、`active_users`、`active_devices`、`login_users` 使用 HLL 非精确去重，对 `old_active_users` 仍做精确 distinct

## 2. 参数约定
- 必填参数：至少传一组周期参数：`dt` / `week` / `month`
- 选填参数：`app_code` / `app_id`、`channel`、`region`、`device`、`user_type`
- 默认过滤逻辑：
  - 传 `dt`：执行日表核查，并按 `dt` 所在自然周 / 自然月联动核查周表与月表
  - 传 `week`：重点核查周表，并抽取该周覆盖的日表窗口做联动比对
  - 传 `month`：重点核查月表，并抽取该月覆盖的日表 / 周表窗口做联动比对
  - 其他维度参数仅用于下钻，不改变最终对账粒度规则

## 3. 绑定程序
- 日表程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_app_user_d/dws_app_user_d.sql`
- 周表程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_app_user_w/dws_app_user_w.sql`
- 月表程序：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_app_user_m/dws_app_user_m.sql`
- 依赖来源：`dwm.dwm_app_user_d`、`dim.dim_user_all`；周表额外依赖 `dim.dim_date_info_all`
- 关键逻辑块：
  - 日表：按 `dwm.dwm_app_user_d` 日事件明细聚合 `new_users / active_users / old_active_users / active_devices / login_users`
  - 周表：按 `dim.dim_date_info_all` 将日事件映射到 `week_of_year + start_of_week` 后做精确 distinct 聚合
  - 月表：按自然月窗口做聚合，其中 `new_users / active_users / active_devices / login_users` 使用 HLL，`old_active_users` 仍为精确 distinct
- 程序维护约定：若来源表、老用户判定、用户类型补齐、周/月窗口口径、HLL 写入口径或主键设计变化，必须同步更新本剧本与 `.claude/database/knowledge.md`

## 4. 核查 parts

### part_01_basic_shape_and_uniqueness
- 目的：确认三张目标表基础形态、主键唯一性、关键空值、值域与负值是否合法
- 来源表：`dws.dws_app_user_d`、`dws.dws_app_user_w`、`dws.dws_app_user_m`
- 核查重点：
  - 指定周期是否有数据
  - 主键字段是否为空
  - 核心指标是否出现负值
  - `device` 是否落在 `IOS / ANDROID / PC / OTHER`
  - 显式输出 `user_type` 风险：同一物理主键下是否存在多个 `user_type`
- 判定：任一关键规则不满足，则该 part 失败

#### SQL：日表基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(new_users) AS total_new_users,
  SUM(active_users) AS total_active_users,
  SUM(old_active_users) AS total_old_active_users,
  SUM(active_devices) AS total_active_devices,
  SUM(login_users) AS total_login_users
FROM dws.dws_app_user_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}};
```

#### SQL：周表基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  MIN(start_of_week) AS min_start_of_week,
  MAX(start_of_week) AS max_start_of_week,
  SUM(new_users) AS total_new_users,
  SUM(active_users) AS total_active_users,
  SUM(old_active_users) AS total_old_active_users,
  SUM(active_devices) AS total_active_devices,
  SUM(login_users) AS total_login_users
FROM dws.dws_app_user_w
WHERE week = '{{week}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}};
```

#### SQL：月表基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(new_users) AS total_new_users,
  SUM(active_users) AS total_active_users,
  SUM(old_active_users) AS total_old_active_users,
  SUM(active_devices) AS total_active_devices,
  SUM(login_users) AS total_login_users
FROM dws.dws_app_user_m
WHERE month = '{{month}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}};
```

#### SQL：日表物理主键重复检查
```sql
SELECT
  dt,
  app_code,
  channel,
  region,
  device,
  COUNT(*) AS dup_cnt
FROM dws.dws_app_user_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
GROUP BY dt, app_code, channel, region, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：周表物理主键重复检查
```sql
SELECT
  week,
  app_code,
  channel,
  region,
  device,
  COUNT(*) AS dup_cnt
FROM dws.dws_app_user_w
WHERE week = '{{week}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
GROUP BY week, app_code, channel, region, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：月表物理主键重复检查
```sql
SELECT
  month,
  app_code,
  channel,
  region,
  device,
  COUNT(*) AS dup_cnt
FROM dws.dws_app_user_m
WHERE month = '{{month}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
GROUP BY month, app_code, channel, region, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：同主键多 user_type 风险样本（优先级最高）
```sql
SELECT
  '{{table_name}}' AS table_name,
  {{period_key}} AS period_key,
  app_code,
  channel,
  region,
  device,
  COUNT(DISTINCT COALESCE(user_type, '__NULL__')) AS user_type_cnt,
  GROUP_CONCAT(DISTINCT COALESCE(user_type, '__NULL__')) AS user_type_list
FROM {{table_name}}
WHERE {{period_filter}}
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
GROUP BY {{period_key}}, app_code, channel, region, device
HAVING COUNT(DISTINCT COALESCE(user_type, '__NULL__')) > 1
LIMIT 100;
```

#### SQL：空值、值域与负值检查
```sql
SELECT *
FROM {{table_name}}
WHERE {{period_filter}}
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}}
  AND (
    app_code IS NULL
    OR channel IS NULL
    OR region IS NULL
    OR device IS NULL
    OR COALESCE(device, '__NULL__') NOT IN ('IOS', 'ANDROID', 'PC', 'OTHER')
    OR COALESCE(new_users, 0) < 0
    OR COALESCE(active_users, 0) < 0
    OR COALESCE(old_active_users, 0) < 0
    OR COALESCE(active_devices, 0) < 0
    OR COALESCE(login_users, 0) < 0
  )
LIMIT 100;
```

### part_02_daily_source_reconciliation
- 目的：按日表实际处理逻辑做全维度来源重算与目标对账
- 来源表：`dwm.dwm_app_user_d`、`dim.dim_user_all`
- 最终对齐粒度：`dt + app_code + channel + region + device + user_type`
- 目标字段：`new_users`、`active_users`、`old_active_users`、`active_devices`、`login_users`
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：日表全维度来源重算
```sql
WITH src AS (
  SELECT
    dau.dt,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_register' THEN dau.uid END) AS src_new_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.uid END) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.device_id END) AS src_active_devices,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_login' THEN dau.uid END) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE dau.dt = '{{dt}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY dau.dt, dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
)
SELECT *
FROM src;
```

#### SQL：日表来源对账异常明细
```sql
WITH src AS (
  SELECT
    dau.dt,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_register' THEN dau.uid END) AS src_new_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.uid END) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.device_id END) AS src_active_devices,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_login' THEN dau.uid END) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE dau.dt = '{{dt}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY dau.dt, dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
),
tgt AS (
  SELECT *
  FROM dws.dws_app_user_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
)
SELECT
  COALESCE(tgt.dt, src.dt) AS dt,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  COALESCE(tgt.user_type, src.user_type) AS user_type,
  tgt.new_users,
  src.src_new_users,
  tgt.active_users,
  src.src_active_users,
  tgt.old_active_users,
  src.src_old_active_users,
  tgt.active_devices,
  src.src_active_devices,
  tgt.login_users,
  src.src_login_users
FROM tgt
FULL OUTER JOIN src
  ON tgt.dt = src.dt
 AND tgt.app_code = src.app_code
 AND tgt.channel = src.channel
 AND tgt.region = src.region
 AND tgt.device = src.device
 AND COALESCE(tgt.user_type, '__NULL__') = COALESCE(src.user_type, '__NULL__')
WHERE
  COALESCE(tgt.new_users, -1) <> COALESCE(src.src_new_users, -1)
  OR COALESCE(tgt.active_users, -1) <> COALESCE(src.src_active_users, -1)
  OR COALESCE(tgt.old_active_users, -1) <> COALESCE(src.src_old_active_users, -1)
  OR COALESCE(tgt.active_devices, -1) <> COALESCE(src.src_active_devices, -1)
  OR COALESCE(tgt.login_users, -1) <> COALESCE(src.src_login_users, -1)
LIMIT 100;
```

### part_03_weekly_source_reconciliation
- 目的：按周表实际处理逻辑做周窗口精确重算与目标对账
- 来源表：`dwm.dwm_app_user_d`、`dim.dim_date_info_all`、`dim.dim_user_all`
- 最终对齐粒度：`week + app_code + channel + region + device + start_of_week + user_type`
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：周表全维度来源重算
```sql
WITH src AS (
  SELECT
    ddi.week_of_year AS week,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    ddi.start_of_week,
    COALESCE(du.user_type, 'normal') AS user_type,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_register' THEN dau.uid END) AS src_new_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.uid END) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.device_id END) AS src_active_devices,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_login' THEN dau.uid END) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dim.dim_date_info_all ddi
    ON dau.dt = ddi.dt
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE ddi.week_of_year = '{{week}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY ddi.week_of_year, dau.app_code, dau.channel, dau.region, dau.device, ddi.start_of_week, COALESCE(du.user_type, 'normal')
)
SELECT *
FROM src;
```

#### SQL：周表来源对账异常明细
```sql
WITH src AS (
  SELECT
    ddi.week_of_year AS week,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    ddi.start_of_week,
    COALESCE(du.user_type, 'normal') AS user_type,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_register' THEN dau.uid END) AS src_new_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.uid END) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.device_id END) AS src_active_devices,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_login' THEN dau.uid END) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dim.dim_date_info_all ddi
    ON dau.dt = ddi.dt
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE ddi.week_of_year = '{{week}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY ddi.week_of_year, dau.app_code, dau.channel, dau.region, dau.device, ddi.start_of_week, COALESCE(du.user_type, 'normal')
),
tgt AS (
  SELECT *
  FROM dws.dws_app_user_w
  WHERE week = '{{week}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
)
SELECT
  COALESCE(tgt.week, src.week) AS week,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  COALESCE(tgt.start_of_week, src.start_of_week) AS start_of_week,
  COALESCE(tgt.user_type, src.user_type) AS user_type,
  tgt.new_users,
  src.src_new_users,
  tgt.active_users,
  src.src_active_users,
  tgt.old_active_users,
  src.src_old_active_users,
  tgt.active_devices,
  src.src_active_devices,
  tgt.login_users,
  src.src_login_users
FROM tgt
FULL OUTER JOIN src
  ON tgt.week = src.week
 AND tgt.app_code = src.app_code
 AND tgt.channel = src.channel
 AND tgt.region = src.region
 AND tgt.device = src.device
 AND tgt.start_of_week = src.start_of_week
 AND COALESCE(tgt.user_type, '__NULL__') = COALESCE(src.user_type, '__NULL__')
WHERE
  COALESCE(tgt.new_users, -1) <> COALESCE(src.src_new_users, -1)
  OR COALESCE(tgt.active_users, -1) <> COALESCE(src.src_active_users, -1)
  OR COALESCE(tgt.old_active_users, -1) <> COALESCE(src.src_old_active_users, -1)
  OR COALESCE(tgt.active_devices, -1) <> COALESCE(src.src_active_devices, -1)
  OR COALESCE(tgt.login_users, -1) <> COALESCE(src.src_login_users, -1)
LIMIT 100;
```

### part_04_monthly_source_reconciliation
- 目的：按月表实际处理逻辑做月窗口重算与目标对账，并专项检查 HLL 写入口径风险
- 来源表：`dwm.dwm_app_user_d`、`dim.dim_user_all`
- 最终对齐粒度：`month + app_code + channel + region + device + user_type`
- 关键规则：
  - 月表使用 HLL，不能简单把日值求和
  - `old_active_users` 仍需精确来源对账
  - 若月表当前 SQL 与字段类型不一致，应显式记为程序风险，不静默忽略
- 判定：任一关键字段或程序一致性检查失败，则该 part 失败

#### SQL：月表程序一致口径重算
```sql
WITH src AS (
  SELECT
    DATE_FORMAT(dau.dt, '%Y%m') AS month,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_register' THEN dau.uid END))) AS src_new_users,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_active' THEN dau.uid END))) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_active' THEN dau.device_id END))) AS src_active_devices,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_login' THEN dau.uid END))) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE DATE_FORMAT(dau.dt, '%Y%m') = '{{month}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY DATE_FORMAT(dau.dt, '%Y%m'), dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
)
SELECT *
FROM src;
```

#### SQL：月表来源对账异常明细
```sql
WITH src AS (
  SELECT
    DATE_FORMAT(dau.dt, '%Y%m') AS month,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_register' THEN dau.uid END))) AS src_new_users,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_active' THEN dau.uid END))) AS src_active_users,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' AND dad.dt IS NULL THEN dau.uid END) AS src_old_active_users,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_active' THEN dau.device_id END))) AS src_active_devices,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_login' THEN dau.uid END))) AS src_login_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dwm.dwm_app_user_d dad
    ON dau.dt = dad.dt
   AND dau.app_code = dad.app_code
   AND dau.channel = dad.channel
   AND dau.uid = dad.uid
   AND dad.event = 'user_register'
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE DATE_FORMAT(dau.dt, '%Y%m') = '{{month}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY DATE_FORMAT(dau.dt, '%Y%m'), dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
),
tgt AS (
  SELECT *
  FROM dws.dws_app_user_m
  WHERE month = '{{month}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
)
SELECT
  COALESCE(tgt.month, src.month) AS month,
  COALESCE(tgt.app_code, src.app_code) AS app_code,
  COALESCE(tgt.channel, src.channel) AS channel,
  COALESCE(tgt.region, src.region) AS region,
  COALESCE(tgt.device, src.device) AS device,
  COALESCE(tgt.user_type, src.user_type) AS user_type,
  tgt.new_users,
  src.src_new_users,
  tgt.active_users,
  src.src_active_users,
  tgt.old_active_users,
  src.src_old_active_users,
  tgt.active_devices,
  src.src_active_devices,
  tgt.login_users,
  src.src_login_users
FROM tgt
FULL OUTER JOIN src
  ON tgt.month = src.month
 AND tgt.app_code = src.app_code
 AND tgt.channel = src.channel
 AND tgt.region = src.region
 AND tgt.device = src.device
 AND COALESCE(tgt.user_type, '__NULL__') = COALESCE(src.user_type, '__NULL__')
WHERE
  COALESCE(tgt.new_users, -1) <> COALESCE(src.src_new_users, -1)
  OR COALESCE(tgt.active_users, -1) <> COALESCE(src.src_active_users, -1)
  OR COALESCE(tgt.old_active_users, -1) <> COALESCE(src.src_old_active_users, -1)
  OR COALESCE(tgt.active_devices, -1) <> COALESCE(src.src_active_devices, -1)
  OR COALESCE(tgt.login_users, -1) <> COALESCE(src.src_login_users, -1)
LIMIT 100;
```

#### SQL：月表 HLL 写入口径 / 类型一致性专项检查
```sql
SELECT
  'dws.dws_app_user_m' AS table_name,
  '程序当前写法使用 hll_union_agg(hll_hash(...))，目标表字段定义为 BIGINT；需确认运行环境是否自动转基数，或程序是否应改为显式 cardinality 输出。' AS risk_note;
```

### part_05_cross_period_consistency
- 目的：联动核查天 / 周 / 月时间窗口覆盖关系与周期键落位是否正确
- 核查重点：
  - 周表 `week/start_of_week` 是否与 `dim.dim_date_info_all` 一致
  - 月表 `month` 是否与日表 `DATE_FORMAT(dt, '%Y%m')` 一致
  - 周/月 distinct 用户数不能简单等于日值求和，但窗口覆盖范围必须一致
- 判定：周期键落位错误则失败；日汇总与周/月天然不可加的 distinct 指标，只做解释性输出

#### SQL：日表到周表窗口落位检查
```sql
WITH daily_scope AS (
  SELECT
    ddi.week_of_year AS week,
    ddi.start_of_week,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    COUNT(DISTINCT CASE WHEN dau.event = 'user_active' THEN dau.uid END) AS daily_window_active_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dim.dim_date_info_all ddi
    ON dau.dt = ddi.dt
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE ddi.week_of_year = '{{week}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY ddi.week_of_year, ddi.start_of_week, dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
)
SELECT
  w.week,
  w.start_of_week,
  w.app_code,
  w.channel,
  w.region,
  w.device,
  w.user_type,
  d.start_of_week AS src_start_of_week,
  w.active_users AS tgt_week_active_users,
  d.daily_window_active_users AS src_week_active_users
FROM dws.dws_app_user_w w
LEFT JOIN daily_scope d
  ON w.week = d.week
 AND w.app_code = d.app_code
 AND w.channel = d.channel
 AND w.region = d.region
 AND w.device = d.device
 AND COALESCE(w.user_type, '__NULL__') = COALESCE(d.user_type, '__NULL__')
WHERE w.week = '{{week}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}}
  AND (
    w.start_of_week <> d.start_of_week
    OR COALESCE(w.active_users, -1) <> COALESCE(d.daily_window_active_users, -1)
  )
LIMIT 100;
```

#### SQL：日表到月表窗口落位检查
```sql
WITH daily_scope AS (
  SELECT
    DATE_FORMAT(dau.dt, '%Y%m') AS month,
    dau.app_code,
    dau.channel,
    dau.region,
    dau.device,
    COALESCE(du.user_type, 'normal') AS user_type,
    hll_cardinality(hll_union(hll_hash(CASE WHEN dau.event = 'user_active' THEN dau.uid END))) AS src_month_active_users
  FROM dwm.dwm_app_user_d dau
  LEFT JOIN dim.dim_user_all du
    ON dau.app_code = du.app_id
   AND dau.uid = du.uid
  WHERE DATE_FORMAT(dau.dt, '%Y%m') = '{{month}}'
    {{app_filter}}
    {{channel_filter}}
    {{region_filter}}
    {{device_filter}}
    {{user_type_filter}}
  GROUP BY DATE_FORMAT(dau.dt, '%Y%m'), dau.app_code, dau.channel, dau.region, dau.device, COALESCE(du.user_type, 'normal')
)
SELECT
  m.month,
  m.app_code,
  m.channel,
  m.region,
  m.device,
  m.user_type,
  m.active_users AS tgt_month_active_users,
  d.src_month_active_users
FROM dws.dws_app_user_m m
LEFT JOIN daily_scope d
  ON m.month = d.month
 AND m.app_code = d.app_code
 AND m.channel = d.channel
 AND m.region = d.region
 AND m.device = d.device
 AND COALESCE(m.user_type, '__NULL__') = COALESCE(d.user_type, '__NULL__')
WHERE m.month = '{{month}}'
  {{app_filter}}
  {{channel_filter}}
  {{region_filter}}
  {{device_filter}}
  {{user_type_filter}}
  AND COALESCE(m.active_users, -1) <> COALESCE(d.src_month_active_users, -1)
LIMIT 100;
```

### part_06_exception_sampling_and_reporting
- 目的：统一输出异常样本，便于开发回归后快速复核
- 必含内容：
  - 日 / 周 / 月各自来源对账异常样本
  - 物理主键重复样本
  - 同主键多 `user_type` 冲突样本
  - 周窗口 `start_of_week` 错位样本
  - 月表 HLL 写入口径风险说明
- 判定：说明性输出，不单独判失败；其结论依赖前述 parts

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_app_user_dwm/`
- 建议文件名：
  - 以 `dt` 驱动：`validate__dt_{{dt}}__{{timestamp}}.md`
  - 以 `week` 驱动：`validate__week_{{week}}__{{timestamp}}.md`
  - 以 `month` 驱动：`validate__month_{{month}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：明确天 / 周 / 月各自是否通过，以及联动核查是否通过
  2. 核查大类汇总：基础形态、日来源对账、周来源对账、月来源对账、跨周期一致性、异常样本
  3. 逐条规则结果：每条规则都要给出核验范围、异常量/样本量、结论
  4. 问题与处理建议：区分程序逻辑错误、主键设计风险、HLL 写入口径风险、周期边界错误
  5. 核心说明：周 / 月 distinct 指标不能简单与日值求和比较，必须按同窗口重算
- 报告中的所有结论都应带数据，不能只写口头判断

## 6. 剧本维护约定
- 该剧本统一绑定 `dws_app_user_d / w / m` 三张表，不再拆成三份重复剧本
- 若日 / 周 / 月任一表改动来源、聚合逻辑、用户类型补齐、老用户判定、周期键、HLL 写法或主键设计，必须同步更新本剧本
- 若后续修复“物理主键未包含 `user_type`”问题，剧本中相关风险 part 需同步改写为回归项
