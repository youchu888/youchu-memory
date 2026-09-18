# dws.dws_app_retention_d_h 用户留存模型设计 + 核查剧本

## 0. 表信息

- **目标对象**：`dws.dws_app_retention_d_h`（**视图**，非物理表）
- **业务名**：用户留存日模型（cohort 注册日 + 30 天留存）
- **业务别名**：留存日表 / cohort retention
- **业务域**：运营平台
- **状态**：developing（等 `dws.dws_app_user_d_h` 上线后启用）
- **粒度**：cohort_dt × app_code × channel × region × device
- **写入语义**：纯视图，查询时实时聚合，无独立 ETL
- **数据环境**：
  - 测试：`.claude/database/test.cnf`
  - 生产：`.claude/database/my.cnf`

## 1. 总览数据流

```
dws.dws_app_user_d_h ─→ dws.dws_app_retention_d_h (视图)
   (BITMAP × 5)            (BIGINT × 31 + update_time)

   cohort_bm = BITMAP_UNION(new_users)        per (dt, dim)
   active_bm = BITMAP_UNION(active_users)     per (dt, app_code)

   dayN 留存 = BITMAP_UNION_COUNT(BITMAP_AND(cohort_bm, active_bm@cohort_dt+N))
```

**核心设计原则**：
1. 留存本质 = "活跃 ∩ 注册" 的派生指标，不维护独立物理表
2. hourly 增量自动继承活跃模型节奏，不需要独立调度
3. schema 完全对齐老 `dws.dws_app_retention_d`（BIGINT + update_time），下游零改动
4. **strict-channel** 口径：留存必须发生在原注册渠道（与 `_d` 老天表一致；跟活跃模型 per-channel 切片对齐），可切换 cross-channel
5. 守恒天然：`dayN_ret_cnt ≤ new_users` 永远成立
6. cohort 维度（channel/region/device）取自注册当时的 dim_user_all，活跃端不限维度

## 2. 视图 DDL

参 `ops_system/04.dws/dws_app_retention_d_h/dws_app_retention_d_h.sql`。

关键结构：
```sql
DROP TABLE IF EXISTS dws.dws_app_retention_d_h;   -- 老 BITMAP 物理表 drop

CREATE VIEW dws.dws_app_retention_d_h AS
WITH
cohort AS (
    SELECT dt AS cohort_dt, app_code, channel, region, device,
           BITMAP_UNION(new_users) AS cohort_bm
    FROM dws.dws_app_user_d_h
    GROUP BY dt, app_code, channel, region, device
),
active_src AS (    -- strict-channel：active 带 channel 维度
    SELECT dt AS active_dt, app_code, channel,
           BITMAP_UNION(active_users) AS active_bm
    FROM dws.dws_app_user_d_h
    GROUP BY dt, app_code, channel
)
SELECT
    c.cohort_dt AS dt, c.app_code, c.channel, c.region, c.device,
    BITMAP_UNION_COUNT(c.cohort_bm) AS new_users,
    BITMAP_UNION_COUNT(IF(a.active_dt = DATE_ADD(c.cohort_dt, INTERVAL 1 DAY),
        BITMAP_AND(c.cohort_bm, a.active_bm), NULL)) AS day1_ret_cnt,
    ... 30 个 dayN ...
    NOW() AS update_time
FROM cohort c
LEFT JOIN active_src a
    ON c.app_code = a.app_code
   AND c.channel  = a.channel
   AND a.active_dt >  c.cohort_dt
   AND a.active_dt <= DATE_ADD(c.cohort_dt, INTERVAL 30 DAY)
GROUP BY c.cohort_dt, c.app_code, c.channel, c.region, c.device;
```

## 3. Schema 对齐对照

| 字段 | 老 `dws_app_retention_d` | 新视图 | 一致性 |
|---|---|---|---|
| `dt` | DATE | DATE | ✅ |
| `app_code` | VARCHAR(50) | VARCHAR(50) | ✅ |
| `channel` | VARCHAR(64) | VARCHAR(64) | ✅ |
| `region` | BIGINT | BIGINT | ✅ |
| `device` | VARCHAR(16) | VARCHAR(16) | ✅ |
| `new_users` | BIGINT | BIGINT (BITMAP_UNION_COUNT) | ✅ |
| `day1_ret_cnt` ~ `day30_ret_cnt` | BIGINT × 30 | BIGINT × 30 | ✅ |
| `update_time` | DATETIME | DATETIME (NOW()) | ✅ |

**唯一不可见差异**：物理表的 BITMAP 列在 SR 内部是 AGGREGATE 状态；视图无聚合状态，查询时即时算。下游 SELECT 完全透明。

## 4. channel 口径选择

| 口径 | 业务含义 | 实现 |
|---|---|---|
| **strict-channel**（默认）| 留存必须发生在原注册渠道 | active_src 带 channel；JOIN 加 `c.channel = a.channel` |
| **cross-channel** | 用户在任何 channel 活跃都算留存 | active_src 不带 channel |

切换 cross-channel 修改：
```sql
active_src AS (
    SELECT dt AS active_dt, app_code,
           BITMAP_UNION(active_users) AS active_bm
    FROM dws.dws_app_user_d_h
    GROUP BY dt, app_code
)
-- JOIN 去掉: AND c.channel = a.channel
```

**默认 strict-channel 的理由**：
1. 与 `dws.dws_app_retention_d` 老天表口径一致 → 数字一致 → 下游零感知切换
2. 与活跃模型 per-channel 切片字段结构一致 → BITMAP_AND 按行 JOIN，无需先 union
3. 广告投放 / 渠道运营场景的"渠道留存"业务定义本就是 strict（带他来的渠道继续活跃）
4. 如要"不限渠道的用户层留存"，可以另起 `GROUP BY dt, app_code` 的 ad-hoc 查询补，不影响默认视图

**活跃模型 channel 的本质**：
- `dws_app_user_d_h.new_users`/`active_users` 行的 channel 来自事件级（注册事件 / page_view 事件自带的 channel 字段）
- 不是"用户的渠道归属"
- 同一 uid 在不同 channel 活跃 → 在多个 (active_dt, channel) 行的 active_users 里都出现（BITMAP hash 只看 (uid, app_id)，跟 channel 无关）
- strict-channel 视图的 BITMAP_AND 自然过滤出"原渠道留存"

## 5. SELECT-only 验证（2026-04-29 测试库）

测试方法：CTE 模拟 `dws_app_user_d_h` 一周数据，套视图聚合，对照老 `dws.dws_app_retention_d`。

### 5.1 cross-channel 版（设计早期默认，仅供参考）

cohort = 2026-04-15（不分维度 totals）：

| 指标 | 视图 (cross) | 老 `_d` 表 (strict) | 差异 |
|---|---|---|---|
| `new_users` | 18,257 | 18,257 | **0** ✅ |
| `day1_ret_cnt` | 1,169 | 1,122 | +47 (+4.2%) |
| `day3_ret_cnt` | 803 | 790 | +13 (+1.6%) |
| `day7_ret_cnt` | 420 | 403 | +17 (+4.2%) |

差异原因：cross-channel 把跨渠道活跃也算进留存。

### 5.2 strict-channel 版（最终方案 / 当前默认）

策略改为 strict-channel 后预期：
- `new_users` 仍 = 18,257（cohort 大小不变）
- `dayN_ret_cnt` 应该跟老 `_d` 表数字非常接近（差异在 ±1% 内，主要来自 dim 缺失的 cohort 取数差异）

> 完整 strict-channel 验证需要等生产 `dws.dws_app_user_d_h` 数据落地后再跑（测试库 dim 空，cohort 取数有妥协）。

### 5.3 共性结论

1. ✅ 视图核心逻辑（BITMAP_AND + dayN 偏移 JOIN）正确
2. ✅ schema BIGINT + update_time 100% 对齐 `_d`
3. ⚠️ 测试库 `dim.dim_user_all` 是空的，cohort 用 register 事件直接代替（妥协）。生产 dim 到位后，cohort 严格按 `register_time = cohort_dt` 来定，跟 `_d` 老表 ROW_NUMBER first-event 逻辑等价

## 6. 上线步骤

| # | 操作 | 验证 |
|---|---|---|
| 1 | 等 `dws.dws_app_user_d_h` 上线并跑稳 1-2 周 + 保留 ≥ 31 天 partition | dim/活跃模型 §7.2 核查 gap=0 |
| 2 | 执行 `dws_app_retention_d_h.sql`：drop 空 BITMAP 表 + create view | `SHOW TABLES` + `DESC dws.dws_app_retention_d_h` |
| 3 | 跑 §7 核查 SQL，与老 `dws.dws_app_retention_d` 对账（strict-channel 默认，差异应在 ±1%）| `new_users` 必须完全对齐 |
| 4 | 下游零感知切换（strict-channel 数字与老表一致）| 各方观察一周 |
| 5 | metadata 状态 `developing → online` | 元数据库 |
| 6 | 老 `dws.dws_app_retention_d` 物理表评估下线（见 §8）| 下游全切到视图后 retire |

## 7. 数据核查规则

### 7.1 视图 vs 老天表对账（strict-channel 口径，差异应在 ±1%）

```sql
-- 选 7 个 cohort 日期对账
WITH cohort_dates AS (
    SELECT DISTINCT dt FROM dws.dws_app_retention_d
    WHERE dt >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
      AND dt <  DATE_SUB(CURDATE(), INTERVAL 23 DAY)
),
new_view AS (
    SELECT dt,
        SUM(new_users)    AS nu_v,
        SUM(day1_ret_cnt) AS d1_v,
        SUM(day7_ret_cnt) AS d7_v
    FROM dws.dws_app_retention_d_h
    WHERE dt IN (SELECT dt FROM cohort_dates)
    GROUP BY dt
),
old_table AS (
    SELECT dt,
        SUM(new_users)    AS nu_o,
        SUM(day1_ret_cnt) AS d1_o,
        SUM(day7_ret_cnt) AS d7_o
    FROM dws.dws_app_retention_d
    WHERE dt IN (SELECT dt FROM cohort_dates)
    GROUP BY dt
)
SELECT
    v.dt,
    v.nu_v, o.nu_o, (v.nu_v - o.nu_o) AS nu_diff,                        -- 必须 = 0
    v.d1_v, o.d1_o, ROUND((v.d1_v - o.d1_o) * 100.0 / o.d1_o, 2) AS d1_diff_pct,
    v.d7_v, o.d7_o, ROUND((v.d7_v - o.d7_o) * 100.0 / o.d7_o, 2) AS d7_diff_pct
FROM new_view v JOIN old_table o ON v.dt = o.dt
ORDER BY v.dt;
-- 期望（strict-channel 默认）：
--   nu_diff = 0（cohort 大小完全一致）
--   dN_diff_pct ∈ ±1%（strict 跟老表口径一致，差异仅来自 dim 同步 lag 等小因素）
```

### 7.2 守恒检查

```sql
-- 留存数必须 ≤ new_users（dayN ⊆ cohort）
SELECT dt, app_code, new_users,
    GREATEST(day1_ret_cnt, day7_ret_cnt, day30_ret_cnt) AS max_ret,
    new_users - GREATEST(day1_ret_cnt, day7_ret_cnt, day30_ret_cnt) AS slack
FROM dws.dws_app_retention_d_h
WHERE dt = '2026-04-01'
  AND GREATEST(day1_ret_cnt, day7_ret_cnt, day30_ret_cnt) > new_users;
-- 期望 0 行（如有 → BITMAP_AND 逻辑 bug）
```

### 7.3 留存单调性参考

```sql
-- day1 >= day3 >= day7 >= day30 通常成立（业务规律，不强制）
SELECT app_code,
    AVG(day1_ret_cnt)  AS d1,
    AVG(day3_ret_cnt)  AS d3,
    AVG(day7_ret_cnt)  AS d7,
    AVG(day30_ret_cnt) AS d30
FROM dws.dws_app_retention_d_h
WHERE dt BETWEEN '2026-03-01' AND '2026-03-31'
  AND app_code REGEXP '^[A-Z]{2,3}-[0-9]{1,4}$'
GROUP BY app_code
ORDER BY d1 DESC LIMIT 20;
```

## 8. 老表迁移路径

| 老表 | 现状 | 处置 |
|---|---|---|
| `dws.dws_app_retention_d_h`（BITMAP 物理表）| developing 空表 | drop → 由本视图替换 |
| `dws.dws_app_retention_d`（BIGINT 物理表）| online，daily 全量回刷 31 天 | 切下游到视图 → retired → drop（下游零改动）|

**切换流程**：
1. `dws_app_user_d_h` 跑稳 + 保留 ≥ 31 天
2. 创建本视图（先用 `_d_h` 名）
3. §7.1 对账 7-14 天 cohort，差异在容忍范围内
4. 业务方确认 cross/strict-channel 口径，决定是否调整
5. 下游消费方逐个切换：`dws.dws_app_retention_d` → `dws.dws_app_retention_d_h`
6. 全部下游切走后，drop 老 `_d` 物理表

**回滚预案**：保留老 `dws.dws_app_retention_d` 调度（disabled），有问题一键 drop view + 重启老调度回填。

## 9. 关键设计决策（review 用）

| 决策 | 选择 | 备选 | 理由 |
|---|---|---|---|
| 物化形式 | **视图** | 物化表 + hourly 跨 partition INSERT | 视图最简单、单一数据源、口径绝对一致；hourly 增量"自动"继承活跃模型 |
| 派生源 | **`dws_app_user_d_h`** | 直接从 dwd 算 | 派生源已是 BITMAP，复用零成本；统一口径 |
| 输出列类型 | **BIGINT** | BITMAP（保留上卷能力）| 留存本身没有"周/月上卷"业务需求（见剧本下方说明）；BIGINT 下游消费简单 |
| channel 口径 | **strict-channel** | cross-channel | 跟 `_d` 老表口径一致 → 下游零感知；跟活跃模型 per-channel 切片自然对齐；广告/渠道运营场景标准定义 |
| 时间窗口 | **30 天** | 90 / 180 天 | 跟现有 `_d` 一致，dws_app_user_d_h 默认保留 30+ 天 |
| `update_time` | NOW() | last_refresh_time | 视图无 refresh，NOW() 表示查询时刻；如下游依赖此值排序请改用别字段 |

## 10. 关于"留存上卷到周/月"的说明

留存指标**本质上不能像 DAU 那样直接上卷**：
- 周留存如果定义为"周 cohort 的 dayN 留存"：可以 BITMAP_UNION 上卷（要 BITMAP 输出）
- 周留存如果定义为"7 天每天 day1 留存数加和"：没有"总人数"语义
- 数字相加（BIGINT SUM）永远是错的

本视图选择 BIGINT 输出，**就放弃了"周/月 cohort 留存上卷"能力**。如果未来业务需要：
- 重新派生一个 `dws.dws_app_retention_w/m_view` 直接从 `dws_app_user_d_h` 上卷（用 BITMAP 中间状态再 BITMAP_UNION_COUNT）
- 不能从本视图再上卷（BIGINT 信息已丢）

实际业务很少需要"周 cohort 的 dayN 留存"，常见展示就是按天 cohort 一行一行铺开（漏斗图），所以 BIGINT 视图够用。

## 11. 性能升级路径（View → Async MV）

视图实时跑要扫 `dws_app_user_d_h` 31 天 partition × 维度组合，per-app/channel/region/device 高基数下可能慢。如业务高频查留存（dashboard），升级为 StarRocks Async 物化视图，**schema 不变，下游零改动**：

```sql
-- 升级时，直接替换 view 为 MV
DROP VIEW dws.dws_app_retention_d_h;

CREATE MATERIALIZED VIEW dws.dws_app_retention_d_h
PARTITION BY dt
DISTRIBUTED BY HASH(app_code) BUCKETS 8
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)        -- 跟活跃模型 hourly 节奏对齐
PROPERTIES (
    "replication_num" = "3",
    "partition_refresh_number" = "2",         -- 一次最多刷 2 个 partition
    "auto_refresh_partitions_limit" = "31"    -- 只维护最近 31 天 partition
)
AS
WITH
cohort AS (
    SELECT dt AS cohort_dt, app_code, channel, region, device,
           BITMAP_UNION(new_users) AS cohort_bm
    FROM dws.dws_app_user_d_h
    GROUP BY dt, app_code, channel, region, device
),
active_src AS (
    SELECT dt AS active_dt, app_code, channel,
           BITMAP_UNION(active_users) AS active_bm
    FROM dws.dws_app_user_d_h
    GROUP BY dt, app_code, channel
)
SELECT
    c.cohort_dt AS dt, c.app_code, c.channel, c.region, c.device,
    BITMAP_UNION_COUNT(c.cohort_bm) AS new_users,
    -- ... 30 个 dayN ...
    NOW() AS update_time
FROM cohort c
LEFT JOIN active_src a
    ON c.app_code = a.app_code
   AND c.channel  = a.channel
   AND a.active_dt >  c.cohort_dt
   AND a.active_dt <= DATE_ADD(c.cohort_dt, INTERVAL 30 DAY)
GROUP BY c.cohort_dt, c.app_code, c.channel, c.region, c.device;
```

**判断升级时机**：
- 业务方反馈查询慢
- 平均 P95 > 5s（通过 SR audit log / pg_stat_statements 类工具采）
- 留存 dashboard 每小时被查 > 100 次

**View vs Async MV 取舍**：

| 维度 | View（默认）| Async MV |
|---|---|---|
| 维护成本 | 零 | 低（refresh 配置 + 监控刷新失败）|
| 实时性 | 实时（基表更新立即可见）| 取决于 refresh 周期（默认 1h）|
| 查询性能 | 慢（每次扫 31 partition）| 快（已物化）|
| 存储成本 | 0 | 跟基表预聚合后数据量级相当 |
| schema 兼容下游 | ✅ 一致 | ✅ 一致（同样 BIGINT + update_time）|
| update_time 语义 | 查询时刻（NOW()）| 该 partition 最近 refresh 时刻 |

**StarRocks MV 类型对照**：
| 类型 | 单/多表 | 刷新机制 | 适用 |
|---|---|---|---|
| Sync MV | 单表 | 写基表时同步 | 单表预聚合 (COUNT/SUM/HLL/BITMAP_UNION)|
| Async MV | 多表 / WITH | 定时 / on-event | 跨表 JOIN、复杂表达式（本场景）|

## 12. 待跟进 / 决策项

1. **生产 `dws.dws_app_user_d_h` 上线 ETA**：等小时模型跑稳 + 保留 31 天 partition 后，本视图才能上线
2. **channel 口径 strict vs cross**：默认 strict（跟老表一致）。如业务方明确要 cross-channel，按 §4 说明改 SQL
3. **老 `dws.dws_app_retention_d` 何时下线**：建议视图上线后并行 1 个月，对账无差再 retire
4. **依赖一致性**：本视图依赖 `dws.dws_app_user_d_h` 字段名 `new_users` / `active_users` / `dt` / `app_code` / `channel` / `region` / `device`。活跃模型如果改 schema，本视图必须同步改
5. **View → MV 升级时机**：先 view 上线，观察查询 P95；如业务高频查留存（dashboard / 月报），按 §11 升级为 Async MV，schema 不变下游零感知

## 13. 维护约定

- 视图 SQL 修改 → 必须先 SELECT-only 跑一遍验证，再 DROP/CREATE VIEW（参 `feedback_etl_validation_via_select_only`）
- 留存数与 `_d` 老表差异超过 5% → 检查 channel 口径或活跃模型 hourly 数据完整性
- per-app 核查只对**合法 app_id**（`^[A-Z]{2,3}-\d{1,4}$`）做（参 `feedback_per_app_verification_rule`）
- 上游活跃模型 partition 数变化（如保留期从 30 天调成 7 天）必须先评估是否影响留存窗口
