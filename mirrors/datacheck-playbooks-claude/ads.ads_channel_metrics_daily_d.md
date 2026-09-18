# ads.ads_channel_metrics_daily_d 数据核查剧本

## 1. 表信息
- 表名：`ads.ads_channel_metrics_daily_d`
- 业务别名：**渠道实时指标表**（app × channel 粒度日度核心大盘）
- 状态：上线
- 粒度：`dt + app_id + channel`，聚合表（AGGREGATE KEY）
- 绑定程序：
  - 批量补齐：`/ops_system/05.ads/job_ads_channel_metrics_daily_d/ads_channel_metrics_daily_d.sql`
  - Flink 实时：`/ops_system/08.flink/flink_all_realtime_watermark_v2_product.sql`
- 源头：多个 DWD 表 UNION ALL，所有 UID 事件 LEFT JOIN `dim.dim_user_all` 取用户级 canonical channel

## 2. 与 `ads_app_metrics_daily_d`（应用实时指标）的关系
- 除了多一个 `channel` 主键 + 落地页专属指标，基本规则一致：
  - 按 app 独立核算；`uid` 相同跨 app 算不同用户
  - 只核对合法 app_id（`^[A-Za-z]+-[0-9]+$`）
  - 登录事件用 `dwd_user_login_d_v2`
- 多出来的指标：`landing_page_pv` / `landing_page_uv` / `landing_page_click_count` / `video_show_from_channel` / `app_entry_count`
- 少的指标：无 `new_reg_ids` 汇总字段（注册拆成 `channel_reg_ids` 按渠道存）

## 3. Channel 归一规则
- **有 uid 的事件**：channel 一律从 `dim.dim_user_all` 取 canonical 值，`COALESCE(dua.channel, 'organic')`
  - 注册、登录、PV、金币消耗、视频事件、订单
- **无 uid 的事件**：直接用事件自带的 channel
  - `dwd_landing_page_view_d.channel`
  - `dwd_landing_page_click.channel` / `dwd_landing_page_click_d.channel`
- **规范化规则**（在 dim_user_all 里已完成）：`NULL / '' / 'self' / 'unknown'` → `'organic'`，首个非 organic 胜出

## 4. 源表映射

| ADS 指标 | 来源 DWD 表 | channel 来源 |
|---|---|---|
| `landing_page_pv` / `landing_page_uv` | `dwd.dwd_landing_page_view_d` | 事件自带 |
| `landing_page_click_count` | `dwd.dwd_landing_page_click` ⚠️ | 事件自带 |
| `video_show_from_channel` | `dwd.dwd_video_event_h`（`video_behavior_key='video_view'`） | dim_user_all |
| `app_entry_count` | `dwd.dwd_app_page_view_d`（`page_key='home'`） | dim_user_all |
| `channel_reg_ids` / `channel_*_reg_ids` | `dwd.dwd_user_register_d_v2` | dim_user_all |
| `login_*_ids` | **`dwd.dwd_user_login_d_v2`** | dim_user_all |
| `user_consume_gold` | `dwd.dwd_coin_consume_h` | dim_user_all |
| `dau_*_ids` | `dwd.dwd_app_page_view_d` 按 uid 去重 | dim_user_all |
| `dad_*_ids` | `dwd.dwd_app_page_view_d` 按 device_id | 事件自带 channel（仍可用） |
| `pay_user_*_ids` / `revenue_*` | `dwd.dwd_order_paid_d` | dim_user_all |
| `order_launch_count` | `dwd.dwd_order_created_h` (ev=created) | dim_user_all |
| `order_valid_count` | `dwd.dwd_order_paid_d` (ev=paid) | dim_user_all |

## 5. 默认参数
- `dt`：默认 T-1
- `app_id` / `channel`：选填抽样

## 6. 核查顺序

### part_01 基础形态
1. 合法 app_id 数量（正则 `^[A-Za-z]+-[0-9]+$`）
2. 每个 app 的 channel 列表是否合理（绝大多数 app 至少有 `organic`）
3. `channel` 不应包含规范化前的脏值（`''` / `NULL` / `'self'` / `'unknown'`）
4. `revenue_total = revenue_channel + revenue_nature`
5. 主键 `(dt, app_id, channel)` 唯一性

### part_02 按 (app, channel) 逐组对 DWD 源头
目标：把 ADS 按 `(app_id, channel)` 分组指标与同粒度 DWD 归一后数据对比。

**核心指标（按 (app, channel) 展开）**：

```sql
WITH legit_apps AS (
  SELECT app_id FROM ads.ads_channel_metrics_daily_d
  WHERE dt='${dt}' AND app_id REGEXP '^[A-Za-z]+-[0-9]+$'
  GROUP BY app_id
),
ads_agg AS (
  SELECT app_id, channel,
    BITMAP_UNION_COUNT(channel_reg_ids) ads_reg,
    BITMAP_UNION_COUNT(login_all_ids) ads_login,
    BITMAP_UNION_COUNT(dau_ids) ads_dau,
    BITMAP_UNION_COUNT(pay_user_ids) ads_pay,
    BITMAP_UNION_COUNT(pay_user_vip_ids) ads_vip,
    BITMAP_UNION_COUNT(pay_user_gold_ids) ads_gold,
    SUM(revenue_total) ads_rev_total,
    SUM(revenue_vip) ads_rev_vip,
    SUM(revenue_gold) ads_rev_gold,
    SUM(revenue_channel) ads_rev_channel,
    SUM(revenue_nature) ads_rev_nature
  FROM ads.ads_channel_metrics_daily_d
  WHERE dt='${dt}' GROUP BY app_id, channel
),
-- 对应 DWD + dim_user_all 归一重算
...
SELECT ...;
```

**对比粒度**：`(app_id, channel)` 逐行对比，而不是 `app_id` 汇总。

### part_03 app 维度总数对 daily 表交叉
目标：`ads_channel_metrics_daily_d` 按 app 聚合 = `ads_app_metrics_daily_d` 对应 app 指标。

```sql
WITH ch AS (
  SELECT app_id,
    BITMAP_UNION_COUNT(login_all_ids) n_login,
    BITMAP_UNION_COUNT(pay_user_ids) n_pay,
    SUM(revenue_total) rev_total
  FROM ads.ads_channel_metrics_daily_d WHERE dt='${dt}' GROUP BY app_id
),
d AS (
  SELECT app_id,
    BITMAP_UNION_COUNT(login_all_ids) n_login,
    BITMAP_UNION_COUNT(pay_user_ids) n_pay,
    SUM(revenue_total) rev_total
  FROM ads.ads_app_metrics_daily_d WHERE dt='${dt}' GROUP BY app_id
)
SELECT ... WHERE ch.<metric> <> d.<metric>;
```

预期：基本吻合（同一 Flink 链路 + 相同归一规则），bitmap 聚合跨 channel union count 与不分 channel 的 count 应完全一致。

### part_04 落地页指标专项
目标：`landing_page_pv` / `landing_page_uv` / `landing_page_click_count` 因无 uid 归一，直接对事件自带 channel 核对。

1. `SUM(landing_page_pv)` vs `COUNT(*) FROM dwd.dwd_landing_page_view_d WHERE dt='${dt}'`，按 (app, channel) 分组逐行
2. `BITMAP_UNION_COUNT(landing_page_uv)` vs `COUNT(DISTINCT uid) FROM dwd.dwd_landing_page_view_d` —— 注意 uid 为空会进 `to_bitmap(null)`
3. `SUM(landing_page_click_count)` vs `dwd.dwd_landing_page_click.date_key='${dt}'` 行数

### part_05 表内 sanity
- `channel_reg_ids` = `channel_ios_reg_ids ∪ channel_android_reg_ids ∪ channel_pc_reg_ids ∪ channel_other_reg_ids`
- `login_all_ids >= login_ios_ids ∪ android ∪ pc ∪ other`
- `dau_ids >= login_all_ids`
- `pay_user_ids >= pay_user_vip_ids` 且 `pay_user_ids >= pay_user_gold_ids`
- `revenue_total >= revenue_vip + revenue_gold`
- `revenue_total = revenue_channel + revenue_nature`
- `dau_vip_ids ∪ dau_non_vip_ids <= dau_ids`（仍有用户 type 未识别会使并集略小）

### part_06 结论输出规范
- 合法 app 数 / 非法 app 数 / 合法 (app, channel) 组合数
- 按 (app, channel) 粒度列不一致指标 TOP N
- ETL bug（如 JHA-160 order_type 历史值）
- 口径差异（如 revenue_channel / revenue_nature 归一边界）
- 待追查疑点

## 7. 已知问题 & 待追查

- **JHA-160 VIP/金币分类缺失**：order_type 为 `'VIP'` / `'金币'`，ADS ETL 只识别 `'vip_subscription'` / `'coin_purchase'`
- **落地页点击使用旧表**：ETL 写的是 `dwd.dwd_landing_page_click`（记忆中已标记"非本项目"），项目标准是 `dwd.dwd_landing_page_click_d`。两表数据量不同，需确认 ETL 修复方向

## 8. 维护约定
- ADS SQL 里字段映射、channel 归一、order_type 判断变更时同步更新。
- 落地页/视频/登录源表切换时同步更新 source mapping。
- 新 `order_type` 引入必须同步更新 VIP/金币分类兼容范围。
