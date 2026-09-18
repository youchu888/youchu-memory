# ads.ads_app_metrics_daily_d 核查剧本

## 1. 表信息
- 表名：`ads.ads_app_metrics_daily_d`
- 业务名：**实时指标天表**（用户口径）；元数据 display_name：**APP日度核心指标全量大盘表**
- 状态：上线
- 粒度：`dt + app_id`（每 app 每天一行）
- 模型：StarRocks `AGGREGATE KEY(dt, app_id)`；bitmap 列 `BITMAP_UNION`，度量列 `SUM`
- 分区：`dt` 动态分区（`Asia/Shanghai`）

## 2. 与相关表的关系
| 表 | 关系 |
|---|---|
| `ads.ads_app_metrics_hourly_d` | 小时实时表；Flink 日间写入；日终批可补数 |
| `ads.ads_product_day_stat_d` | **下游**：项目日报的 DAU/注册 bitmap 来源 |
| `dws.dws_app_user_d_h` | **不同口径**：DWS 多维活跃模型（channel/region/device 切片）；**不是**本表替代品 |

## 3. 绑定程序
- 日终批（权威 T-1 重算）：`/ops_system/05.ads/job_ads_app_metrics_daily_d/ads_app_metrics_daily_d.sql`
- DDL：`/ops_system/05.ads/job_ads_app_metrics_daily_d/ads_app_metrics_daily_d_ddl.sql`
- Flink 实时（日间）：`/ops_system/08.flink/flink_all_realtime_watermark_v2_product.sql` 等
- 小时表 DDL/SQL：`/ops_system/05.ads/job_ads_app_metrics_hourly_d/`

DDL 注释：**日间 Flink 实时计算，日终重新计算 T-1 数据**。

## 4. 参数约定
- 必填：`dt`（`yyyy-MM-dd`）
- 选填：`app_id`（**不是** `app_code`）
- 批处理分区宏：`INSERT OVERWRITE ... PARTITION (p${pt})`，`${dt}` 为统计日

## 5. 字段分组（50 列）

### 5.1 维度
| 字段 | 说明 |
|---|---|
| `dt` | 统计日期 |
| `app_id` | 应用唯一标识（如 `TJ-001`） |

### 5.2 注册（uid bitmap）
`new_reg_ids`、`new_reg_channel_ids`、`new_reg_nature_ids`、`new_reg_ios_ids`、`new_reg_android_ids`、`new_reg_pc_ids`、`new_reg_other_ids`

### 5.3 登录 / 用户活跃（uid bitmap）
`login_all_ids`、`login_ios_ids`、`login_android_ids`、`login_pc_ids`、`login_other_ids`  
`dau_ids`、`dau_ios_ids`、`dau_android_ids`、`dau_pc_ids`、`dau_other_ids`  
`dau_vip_ids`、`dau_non_vip_ids`

### 5.4 设备活跃（device_id bitmap，DAD）
`dad_ids`、`dad_ios_ids`、`dad_android_ids`、`dad_pc_ids`、`dad_other_ids`  
`dad_vip_ids`、`dad_no_vip_ids`

### 5.5 交易用户（uid bitmap）
`pay_user_ids`、`pay_user_gold_ids`、`pay_user_vip_ids`

### 5.6 累加度量（SUM，bigint）
`active_duration_total`（秒）、`order_launch_count`、`order_valid_count`  
`revenue_total` / `revenue_channel` / `revenue_nature` / `revenue_gold` / `revenue_vip`（**分**）  
`user_consume_gold`、`video_view_duration`（秒）、`video_detail_pv`、`video_play_pv`、`video_complete_pv`  
`video_like_count`、`video_comment_count`、`video_collect_count`、`video_pay_coin_count`  
`ad_click_count`、`open_count`

## 6. 核心口径（来自 ETL SQL）

### 6.1 活跃归因（`dwd.dwd_app_page_view_d`）
- **uid 维度**（`uid_attribution`）：按 `(app_id, uid)` 取 `MAX_BY(user_type/device, event_time)` 作为当日最终身份/终端
- **device 维度**（`did_attribution`）：按 `(app_id, device_id)` 同样取最终身份/终端
- **DAU**：有 page_view 的 uid → `bitmap_hash64_udf(uid)`
- **DAD（设备日活）**：有 page_view 且 `device_id IS NOT NULL` → `bitmap_hash64_udf(device_id)`
- 终端归一：`IOS` / `ANDROID` / `PC` / `OTHER`（`UPPER(TRIM(device))`）
- VIP 拆分：`final_user_type = 'VIP'` vs `'NORMAL'`

### 6.2 注册（`dwd.dwd_user_register_d_v2` + `dim.dim_user_all`）
- channel 归一：`COALESCE(dim_user_all.channel, 'organic')`
- 渠道注册：`channel NOT IN ('', 'organic') AND channel IS NOT NULL`
- 自然注册：其余

### 6.3 其他分支（UNION ALL）
- 交易：`dwd_order_created_h` / `dwd_order_paid_d`
- 视频：`dwd_video_event_h` 等
- 登录：`dwd_user_login_d_v2`
- 广告点击：`dwd_ad_click_h`
- 金币消耗：`dwd_coin_consume_h`

### 6.4 与项目日报的 DAU 规则（消费方 `ads_product_day_stat_d`）
- `new_dau_count = new_reg_count`（新用户日活 = 新注册）
- `dau_count = old_dau_count + new_dau_count`（日活 = 老活跃 + 新注册）
- bitmap 运算需 `ifnull(..., bitmap_empty())` 兜底

## 7. 标准查询模板

### 7.1 单 app 日活 / 设备日活
```sql
SELECT
  dt,
  app_id,
  BITMAP_COUNT(dau_ids)              AS dau,
  BITMAP_COUNT(new_reg_ids)            AS new_reg,
  BITMAP_COUNT(dad_ids)                AS dad,          -- 设备日活
  BITMAP_COUNT(dad_ios_ids)            AS dad_ios,
  BITMAP_COUNT(dad_android_ids)        AS dad_android,
  BITMAP_COUNT(dad_pc_ids)             AS dad_pc
FROM ads.ads_app_metrics_daily_d
WHERE dt = '@{dt}'
  AND app_id = '@{app_id}';
```

### 7.2 多 app 对比
```sql
SELECT dt, app_id,
  BITMAP_COUNT(dau_ids) AS dau,
  BITMAP_COUNT(dad_ids) AS dad
FROM ads.ads_app_metrics_daily_d
WHERE dt BETWEEN '@{dt_start}' AND '@{dt_end}'
  AND app_id IN (@{app_id_list})
ORDER BY dt, app_id;
```

### 7.3 bitmap 合集（跨字段）
```sql
BITMAP_COUNT(BITMAP_OR(
  IFNULL(dau_ids, BITMAP_EMPTY()),
  IFNULL(new_reg_ids, BITMAP_EMPTY())
))
```

## 8. 与 `dws.dws_app_user_d_h` 的差异（重要）

| 维度 | 实时指标天表 | DWS 活跃模型 |
|---|---|---|
| 业务叫法 | 实时指标天表 / 产品指标表 | 用户活跃小时模型 |
| 粒度 | `dt + app_id` | `dt + app_code + channel + region + device + user_type` |
| 项目字段名 | **`app_id`** | **`app_code`** |
| uid 日活 | `BITMAP_COUNT(dau_ids)` | `BITMAP_UNION_COUNT(active_users)` |
| 设备日活 | **`BITMAP_COUNT(dad_ids)`** | `BITMAP_UNION_COUNT(active_devices)` |
| device hash | `bitmap_hash64_udf(device_id)` | `bitmap_hash64_udf(CONCAT(device_id,'@',app_id))` |
| 活跃事件 | `dwd_app_page_view_d` 全量 page_view | 活跃模型事件过滤（ACTIVE 等） |

**查「某 app 设备日活」应优先本表 `dad_ids`，不要用 DWS `active_devices` 代替。**

## 9. 核查 parts

### part_01_dad_vs_dwd
- 目的：设备日活与 DWD 直算对齐（本表设计目标）
```sql
WITH ads AS (
  SELECT dt, app_id, BITMAP_COUNT(dad_ids) AS dad
  FROM ads.ads_app_metrics_daily_d
  WHERE dt = '@{dt}' AND app_id = '@{app_id}'
),
dwd AS (
  SELECT dt, app_id, COUNT(DISTINCT device_id) AS dad
  FROM dwd.dwd_app_page_view_d
  WHERE dt = '@{dt}' AND app_id = '@{app_id}'
    AND device_id IS NOT NULL AND device_id != ''
  GROUP BY dt, app_id
)
SELECT a.dt, a.app_id, a.dad AS ads_dad, d.dad AS dwd_dad,
       a.dad - d.dad AS diff
FROM ads a
JOIN dwd d ON a.dt = d.dt AND a.app_id = d.app_id;
```
- 判定：`diff = 0` 为通过（2026-05-27 生产 TJ-001/TJ-011 已验证一致）

### part_02_dau_subtotal
- 目的：DAU 分端之和与总量（允许 OTHER 存在；跨端同 uid 可能不完全可加）
```sql
SELECT dt, app_id,
  BITMAP_COUNT(dau_ids) AS dau_total,
  BITMAP_COUNT(dau_ios_ids) + BITMAP_COUNT(dau_android_ids)
    + BITMAP_COUNT(dau_pc_ids) + BITMAP_COUNT(dau_other_ids) AS dau_sum_parts
FROM ads.ads_app_metrics_daily_d
WHERE dt = '@{dt}' AND app_id = '@{app_id}';
```

### part_03_downstream_product_day_stat
- 目的：与项目日报注册/DAU bitmap 一致（见 `ads.ads_product_day_stat_d` playbook part_02）

## 10. 生产数据快照（2026-05-29 核查）
| dt | app_id | dau | dad |
|---|---|---:|---:|
| 2026-05-27 | TJ-001 | 6,144 | 9,357,917 |
| 2026-05-28 | TJ-001 | 5,916 | 9,408,704 |
| 2026-05-27 | TJ-011 | 63,488 | 568,276 |
| 2026-05-28 | TJ-011 | 66,030 | 578,831 |

分区覆盖（TJ-001/TJ-011）：`2025-12-22` ~ `2026-05-29`。
