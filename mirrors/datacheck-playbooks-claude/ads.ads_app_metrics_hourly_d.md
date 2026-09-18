# ads.ads_app_metrics_hourly_d 数据核查剧本

## 1. 表信息
- 表名：`ads.ads_app_metrics_hourly_d`
- 业务别名：**应用小时汇总实时指标**（app × 小时 粒度核心大盘）
- 状态：上线
- 粒度：`dt + hr + app_id`，聚合表（AGGREGATE KEY），bitmap 字段走 BITMAP_UNION
- 绑定程序：
  - Flink 实时：`/ops_system/08.flink/flink_all_realtime_watermark_v2_product.sql`
  - 批量补齐：`/ops_system/05.ads/job_ads_app_metrics_hourly_d/ads_app_metrics_hourly_d.sql`
- 源头：`dw.dw_user_event_detail`（Flink 侧直接从 Kafka 消费相同明细；批量侧从 DWD 表补齐）

## 2. 与 `ads_app_metrics_daily_d`（应用实时指标）的关系
- 除了粒度多了 `hr` 之外，指标定义、源表映射、`order_type` 兼容、渠道归一规则**完全一致**。
- 本剧本复用 [ads.ads_app_metrics_daily_d](ads.ads_app_metrics_daily_d.md) 的所有核查规则，只额外增加小时维度的特殊校验。
- **跨小时合并 ≠ 相加**：bitmap 字段跨小时合并必须先 `BITMAP_UNION` 再 `BITMAP_UNION_COUNT()`，不能把每小时 `BITMAP_UNION_COUNT()` 的结果相加（会重复计数同一用户在多个小时的活跃）。

## 3. 使用前提
- 按 app 独立核算，只核对合法 app_id（`^[A-Za-z]+-[0-9]+$`）。
- 登录源表用 **`dwd_user_login_d_v2`**，旧表 `dwd_user_login_d` 禁用。
- VIP/金币分类要兼容历史 `order_type` 值 `'VIP'` / `'金币'`。

## 4. 默认参数
- `dt`：默认 T-1
- `hr`：选填，不填表示跨全部 24 小时做日度汇总核对

## 5. 核查顺序

### part_01 基础形态
检查项：
1. 每个 `(dt, app_id)` 覆盖 24 个 `hr` 分区（或当日已过时刻），无跳跃
2. 合法 app_id 数量与总 app_id 数量差异
3. `current_online_count` / `online_peak_count` / bitmap 字段非异常值

### part_02 小时汇总 → 日度对比（核心）
目标：把 24 小时聚合为日度，与 DWD 源头逐 app 对比。

**用户类 bitmap 指标**（等同 [daily 剧本 part_02](ads.ads_app_metrics_daily_d.md)）：

```sql
WITH legit_apps AS (
  SELECT app_id FROM ads.ads_app_metrics_hourly_d
  WHERE dt='${dt}' AND app_id REGEXP '^[A-Za-z]+-[0-9]+$'
  GROUP BY app_id
),
ads_agg AS (
  SELECT app_id,
    BITMAP_UNION_COUNT(new_reg_ids) AS ads_new_reg,
    BITMAP_UNION_COUNT(login_all_ids) AS ads_login,
    BITMAP_UNION_COUNT(dau_ids) AS ads_dau,
    BITMAP_UNION_COUNT(pay_user_ids) AS ads_pay,
    BITMAP_UNION_COUNT(pay_user_vip_ids) AS ads_vip,
    BITMAP_UNION_COUNT(pay_user_gold_ids) AS ads_gold,
    SUM(revenue_total) AS ads_revenue,
    SUM(revenue_vip) AS ads_rev_vip,
    SUM(revenue_gold) AS ads_rev_gold
  FROM ads.ads_app_metrics_hourly_d WHERE dt='${dt}'
  GROUP BY app_id
)
-- 与 DWD 源表 COUNT(DISTINCT uid) / SUM(amount) 逐 app 对比
...
```

**源表映射**（与 daily 相同）：

| ADS bitmap 字段 | DWD 源 | 过滤 |
|---|---|---|
| `new_reg_ids` | `dwd.dwd_user_register_d_v2` | `dt=${dt}` |
| `new_reg_channel_ids` | 同上 | 且 `channel IS NOT NULL AND channel<>''` |
| `new_reg_nature_ids` | 同上 | 且 `channel IS NULL OR channel=''` |
| `login_all_ids` | **`dwd.dwd_user_login_d_v2`** | `dt=${dt}` |
| `dau_ids` | `dwd.dwd_app_page_view_d` | `dt=${dt}` 按 `uid` 去重 |
| `pay_user_ids` | `dwd.dwd_order_paid_d` | `dt=${dt}` |
| `pay_user_vip_ids` | `dwd.dwd_order_paid_d` | 且 `order_type IN ('vip_subscription','VIP')` |
| `pay_user_gold_ids` | `dwd.dwd_order_paid_d` | 且 `order_type IN ('coin_purchase','金币')` |

### part_03 小时内独立核对（可选，抽样）
目标：验证单小时汇总与 DWD 小时级数据一致性。

场景：
- 只对有 `event_time`/`date_key` 精确小时信息的 DWD 表可做
- 抽样最近一个已收盘小时即可，不必全覆盖

### part_04 跨小时一致性校验
目标：小时汇总出的日度指标 = `ads_app_metrics_daily_d` 对应 app 的日度指标。

```sql
WITH hourly AS (
  SELECT app_id, BITMAP_UNION_COUNT(login_all_ids) AS cnt
  FROM ads.ads_app_metrics_hourly_d WHERE dt='${dt}' GROUP BY app_id
),
daily AS (
  SELECT app_id, BITMAP_UNION_COUNT(login_all_ids) AS cnt
  FROM ads.ads_app_metrics_daily_d WHERE dt='${dt}' GROUP BY app_id
)
SELECT h.app_id, h.cnt AS hourly_cnt, d.cnt AS daily_cnt, h.cnt - d.cnt AS diff
FROM hourly h JOIN daily d USING(app_id)
WHERE h.cnt <> d.cnt;
```

预期：所有 app 两表完全一致（Flink 同源写入）。如有差异，优先排查：
- 一张表有分区补齐延迟、另一张已更新
- hourly 有 `hr=NULL` 或异常小时残留

### part_05 表内 sanity
- `dau_ids >= login_all_ids`
- `pay_user_ids >= pay_user_vip_ids` 且 `pay_user_ids >= pay_user_gold_ids`
- `revenue_total = revenue_channel + revenue_nature`
- `new_reg_ids = new_reg_channel_ids + new_reg_nature_ids`
- `online_peak_count <= MAX(current_online_count)`

### part_06 结论输出规范
同 [daily 剧本 part_06](ads.ads_app_metrics_daily_d.md)。

## 6. 维护约定
- Flink/批量程序逻辑变更时同步更新。
- 与 daily 剧本保持指标映射一致；若两者发散，先更新本剧本并说明原因。
