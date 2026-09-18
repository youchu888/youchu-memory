# dws.dws_user_reg_video_funnel_daily_d 核查剧本

## 1. 表信息
- 表名：`dws.dws_user_reg_video_funnel_daily_d`
- 业务名：视频漏斗模型表
- 状态：上线
- 表说明：按注册 cohort 沉淀 app 用户在注册后 24 小时内的严格串行视频漏斗事实表
- 目标粒度：`dt + app_code + channel + device`
- 核心指标：`new_users`、`page_view_user_cnt`、`video_exposure_user_cnt`、`first_play_user_cnt`
- 关键说明：
  - `dt` 表示**注册日期**，不是行为日期
  - 只允许使用 `dwd.dwd_user_register_d_v2`、`dwd.dwd_app_page_view_d`、`dwd.dwd_video_event_h` 三张来源表（_h 版本已作废）
  - **channel 取自 `dim.dim_user_all`**（first-non-organic-wins），不取自注册事件自带的 channel 字段
  - 默认维度包含 `app_id`，在目标表字段中命名为 `app_code`
  - 漏斗按**严格串行顺序**定义：`register_time < page_view_reach_time < video_exposure_time < first_play_time`
  - `page_view_reach_time` 指注册后 24 小时内的**第 3 次**页面浏览时间
  - `video_exposure_user_cnt` 要求浏览达标后存在 `video_view`
  - `first_play_user_cnt` 要求曝光后存在 `video_play` 且 `play_duration >= 5`

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_code` / `app_id`、`channel`、`device`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该注册日全量 app 的全维度结果
  - 传 `dt + app_code/app_id`：核查指定 app
  - 其他维度参数仅用于下钻，不改变最终对账粒度规则

## 3. 绑定程序
- 绑定处理程序（DDL）：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_user_reg_video_funnel_daily_d/dws_user_reg_video_funnel_daily_d_ddl.sql`
- 绑定处理程序（ETL）：`/Users/arthur/Program/datacenter/dc-parent/ops_system/04.dws/dws_user_reg_video_funnel_daily_d/dws_user_reg_video_funnel_daily_d.sql`
- 当前绑定说明：`/datacheck` 执行视频漏斗模型表核查时，默认以该 SQL 的已上线实现为程序参考。
- 关键逻辑块：
  - `reg_base`：按 `dt + app_id + uid` 取首条注册事件，完成渠道/设备归一
  - `page_view_hit`：在注册后 24 小时内识别第 3 次浏览时间
  - `video_exposure_hit`：在浏览达标之后识别首条 `video_view`
  - `first_play_hit`：在曝光之后识别首条 `video_play AND play_duration >= 5`
  - 最终 `GROUP BY`：按 `dt + app_code + channel + device` 聚合
- 已确认逻辑：
  - 注册去重规则：`ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time, event_id)`
  - 行为关联键：`app_id + uid`
  - **渠道归一：从 `dim.dim_user_all` 取**，`COALESCE(dua.channel, 'organic')`（dim 已统一归一，上游脏值在 dim 层 / DWD 层已处理）
  - 设备归一：`IOS / ANDROID / PC / OTHER`
  - 时间窗：所有阶段都必须满足注册后 24 小时内
  - 串行顺序：阶段之间使用严格大于 `>`
  - 调度策略：小时任务重刷 `T-1`，凌晨收口任务重刷 `T-2`
- 程序维护约定：若注册去重、行为来源、串行顺序、24 小时窗口、设备归一、渠道归一或调度分区策略变化，必须同步更新本剧本与 `.claude/database/knowledge.md`

## 4. 核查 parts

### part_01_basic_shape_and_monotonicity
- 目的：确认目标表基础形态、主键唯一性、空值、负值与漏斗单调性是否正常
- 来源表：`dws.dws_user_reg_video_funnel_daily_d`
- 核查重点：
  - 指定日期是否有数据
  - 主键 `dt + app_code + channel + device` 是否唯一
  - 主键字段是否为空
  - `device` 是否仅出现 `IOS / ANDROID / PC / OTHER`
  - 指标是否出现负值
  - 是否满足 `new_users >= page_view_user_cnt >= video_exposure_user_cnt >= first_play_user_cnt`
- 判定：任一关键字段为空、主键重复、负值或漏斗单调性被破坏，则该 part 失败

#### SQL：基础分布
```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT app_code) AS app_cnt,
  SUM(new_users) AS total_new_users,
  SUM(page_view_user_cnt) AS total_page_view_user_cnt,
  SUM(video_exposure_user_cnt) AS total_video_exposure_user_cnt,
  SUM(first_play_user_cnt) AS total_first_play_user_cnt
FROM dws.dws_user_reg_video_funnel_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{device_filter}};
```

#### SQL：主键重复检查
```sql
SELECT
  dt,
  app_code,
  channel,
  device,
  COUNT(*) AS dup_cnt
FROM dws.dws_user_reg_video_funnel_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{device_filter}}
GROUP BY dt, app_code, channel, device
HAVING COUNT(*) > 1
LIMIT 100;
```

#### SQL：空值、值域、负值与漏斗顺序检查
```sql
SELECT *
FROM dws.dws_user_reg_video_funnel_daily_d
WHERE dt = '{{dt}}'
  {{app_filter}}
  {{channel_filter}}
  {{device_filter}}
  AND (
    app_code IS NULL
    OR channel IS NULL
    OR device IS NULL
    OR COALESCE(device, '__NULL__') NOT IN ('IOS', 'ANDROID', 'PC', 'OTHER')
    OR COALESCE(new_users, 0) < 0
    OR COALESCE(page_view_user_cnt, 0) < 0
    OR COALESCE(video_exposure_user_cnt, 0) < 0
    OR COALESCE(first_play_user_cnt, 0) < 0
    OR COALESCE(page_view_user_cnt, 0) > COALESCE(new_users, 0)
    OR COALESCE(video_exposure_user_cnt, 0) > COALESCE(page_view_user_cnt, 0)
    OR COALESCE(first_play_user_cnt, 0) > COALESCE(video_exposure_user_cnt, 0)
  )
LIMIT 100;
```

### part_02_full_grain_source_reconciliation
- 目的：按真实处理逻辑做全维度来源重算与目标对账
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_app_page_view_d`、`dwd.dwd_video_event_h`、`dim.dim_user_all`（channel 归一源）
- 最终对齐粒度：`dt + app_code + channel + device`
- 目标字段：`new_users`、`page_view_user_cnt`、`video_exposure_user_cnt`、`first_play_user_cnt`
- 关键规则：
  - 只允许 3 张 DWD 来源表参与重算 + 1 张 dim 取 channel
  - 注册 cohort 必须先按 `dt + app_id + uid` 做首条注册去重
  - **channel 从 `dim.dim_user_all` 取**：`COALESCE(dua.channel, 'organic')`
  - 第 3 次浏览时间必须在注册后 24 小时内
  - 曝光必须发生在浏览达标之后
  - 有效播放必须发生在曝光之后，且 `play_duration >= 5`
  - distinct 用 `COUNT(DISTINCT CONCAT(app_code, '|', uid))`，不能只 `COUNT(DISTINCT uid)`（同 uid 可能跨 app_code）
- 判定：任一目标字段与来源重算在全维度上不一致，则该 part 失败

#### SQL：全维度来源重算
```sql
WITH reg_base AS (
  SELECT
    t1.dt,
    t1.app_id AS app_code,
    COALESCE(dua.channel, 'organic') AS channel,
    CASE WHEN UPPER(TRIM(t1.device)) = 'IOS' THEN 'IOS' WHEN UPPER(TRIM(t1.device)) = 'ANDROID' THEN 'ANDROID' WHEN UPPER(TRIM(t1.device)) = 'PC' THEN 'PC' ELSE 'OTHER' END AS device,
    t1.uid,
    t1.event_time AS register_time
  FROM (
    SELECT
      dt,
      app_id,
      device,
      uid,
      event_time,
      event_id,
      ROW_NUMBER() OVER (PARTITION BY dt, app_id, uid ORDER BY event_time, event_id) AS rn
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = '{{dt}}'
      {{app_filter}}
      AND app_id IS NOT NULL
      AND app_id != ''
      AND uid IS NOT NULL
      AND uid != ''
      AND event_time IS NOT NULL
  ) t1
  LEFT JOIN dim.dim_user_all dua
    ON t1.app_id = dua.app_id AND t1.uid = dua.uid
  WHERE t1.rn = 1
),
page_view_ranked AS (
  SELECT
    reg.dt,
    reg.app_code,
    reg.channel,
    reg.device,
    reg.uid,
    reg.register_time,
    pv.event_time,
    ROW_NUMBER() OVER (PARTITION BY reg.dt, reg.app_code, reg.uid ORDER BY pv.event_time, pv.event_id) AS pv_rn
  FROM reg_base reg
  JOIN dwd.dwd_app_page_view_d pv
    ON pv.app_id = reg.app_code
   AND pv.uid = reg.uid
   AND pv.dt IN ('{{dt}}', DATE_ADD('{{dt}}', INTERVAL 1 DAY))
   AND pv.event_time > reg.register_time
   AND pv.event_time < DATE_ADD(reg.register_time, INTERVAL 24 HOUR)
),
page_view_hit AS (
  SELECT
    dt,
    app_code,
    channel,
    device,
    uid,
    register_time,
    event_time AS page_view_reach_time
  FROM page_view_ranked
  WHERE pv_rn = 3
),
video_exposure_ranked AS (
  SELECT
    pv.dt,
    pv.app_code,
    pv.channel,
    pv.device,
    pv.uid,
    pv.register_time,
    pv.page_view_reach_time,
    ve.event_time AS video_exposure_time,
    ROW_NUMBER() OVER (PARTITION BY pv.dt, pv.app_code, pv.uid ORDER BY ve.event_time, ve.hour, ve.event_id) AS exposure_rn
  FROM page_view_hit pv
  JOIN dwd.dwd_video_event_h ve
    ON ve.app_id = pv.app_code
   AND ve.uid = pv.uid
   AND ve.dt IN ('{{dt}}', DATE_ADD('{{dt}}', INTERVAL 1 DAY))
   AND ve.video_behavior_key = 'video_view'
   AND ve.event_time > pv.page_view_reach_time
   AND ve.event_time < DATE_ADD(pv.register_time, INTERVAL 24 HOUR)
),
video_exposure_hit AS (
  SELECT
    dt,
    app_code,
    channel,
    device,
    uid,
    register_time,
    page_view_reach_time,
    video_exposure_time
  FROM video_exposure_ranked
  WHERE exposure_rn = 1
),
first_play_ranked AS (
  SELECT
    vv.dt,
    vv.app_code,
    vv.channel,
    vv.device,
    vv.uid,
    vp.event_time AS first_play_time,
    ROW_NUMBER() OVER (PARTITION BY vv.dt, vv.app_code, vv.uid ORDER BY vp.event_time, vp.hour, vp.event_id) AS play_rn
  FROM video_exposure_hit vv
  JOIN dwd.dwd_video_event_h vp
    ON vp.app_id = vv.app_code
   AND vp.uid = vv.uid
   AND vp.dt IN ('{{dt}}', DATE_ADD('{{dt}}', INTERVAL 1 DAY))
   AND vp.video_behavior_key = 'video_play'
   AND COALESCE(vp.play_duration, 0) >= 5
   AND vp.event_time > vv.video_exposure_time
   AND vp.event_time < DATE_ADD(vv.register_time, INTERVAL 24 HOUR)
),
first_play_hit AS (
  SELECT
    dt,
    app_code,
    channel,
    device,
    uid
  FROM first_play_ranked
  WHERE play_rn = 1
)
SELECT
  reg.dt,
  reg.app_code,
  reg.channel,
  reg.device,
  COUNT(DISTINCT CONCAT(reg.app_code, '|', reg.uid)) AS src_new_users,
  COUNT(DISTINCT CONCAT(pv.app_code, '|', pv.uid)) AS src_page_view_user_cnt,
  COUNT(DISTINCT CONCAT(vv.app_code, '|', vv.uid)) AS src_video_exposure_user_cnt,
  COUNT(DISTINCT CONCAT(fp.app_code, '|', fp.uid)) AS src_first_play_user_cnt
FROM reg_base reg
LEFT JOIN page_view_hit pv
  ON reg.dt = pv.dt
 AND reg.app_code = pv.app_code
 AND reg.channel = pv.channel
 AND reg.device = pv.device
 AND reg.uid = pv.uid
LEFT JOIN video_exposure_hit vv
  ON reg.dt = vv.dt
 AND reg.app_code = vv.app_code
 AND reg.channel = vv.channel
 AND reg.device = vv.device
 AND reg.uid = vv.uid
LEFT JOIN first_play_hit fp
  ON reg.dt = fp.dt
 AND reg.app_code = fp.app_code
 AND reg.channel = fp.channel
 AND reg.device = fp.device
 AND reg.uid = fp.uid
GROUP BY reg.dt, reg.app_code, reg.channel, reg.device;
```

### part_03_abnormal_app_drilldown
- 目的：对 page_view 为 0 或整条漏斗为 0 的 app 做异常定位
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_app_page_view_d`、`dwd.dwd_video_event_h`、`dim.dim_user_all`
- 核查重点：
  - 注册基数
  - 注册后 24 小时内是否存在任意 `app_page_view`
  - 是否能达到第 3 次浏览
  - 是否存在任意 `video_view`
  - 是否存在任意 `video_play AND play_duration >= 5`
  - 严格串行漏斗各阶段是否为 0
- 判定：用于异常定位，不直接作为表失败结论

#### SQL：异常 app 快速定位
```sql
-- 传入 {{dt}} 与 {{app_filter}}，复用 part_02 的 reg_base / page_view_hit / video_exposure_hit / first_play_hit
-- 补充输出：
-- register_user_cnt / any_page_view_user_cnt / reach_3_page_view_user_cnt /
-- any_video_view_user_cnt / any_video_play_ge5_user_cnt /
-- strict_new_users / strict_page_view_user_cnt / strict_video_exposure_user_cnt / strict_first_play_user_cnt
```
