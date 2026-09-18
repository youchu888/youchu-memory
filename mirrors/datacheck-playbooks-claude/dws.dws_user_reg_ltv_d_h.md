# dws.dws_user_reg_ltv_d_h 用户生命价值（LTV）模型设计 + 核查剧本

## 0. 表信息

- **目标对象**：`dws.dws_user_reg_ltv_d_h`（**Async 物化视图**，非物理表）
- **业务名**：用户生命价值 LTV 日模型（cohort 注册日 + 30 天充值金额）
- **业务别名**：注册 LTV / D0~D30 充值金额
- **业务域**：运营平台 / 商业分析
- **状态**：developing
- **粒度**：cohort_dt × app_code × channel × region × device
- **写入语义**：Async MV，每小时刷新最近 31 天 partition；查询时直接读物化结果（毫秒级响应）
- **数据环境**：
  - 测试：`.claude/database/test.cnf`
  - 生产：`.claude/database/my.cnf`

## 1. 总览数据流

```
dim.dim_user_all (register_time / register_channel / device / 地区) ─┐
dim.dim_region_info_all                                              ├─→ cohort 维度
                                                                     │
dwd.dwd_order_paid_d (order_type IN vip/coin AND event=order_paid) ──┼─→ pay (uid, amount)
                                                                     │
                                                       JOIN by (app_id, uid)
                                                       filter pay_dt ∈ [cohort_dt, cohort_dt+30]
                                                       SUM amount per cohort × dim × day_offset
                                                                     ↓
                                                  dws.dws_user_reg_ltv_d_h (Async MV, hourly refresh)
                                                  schema = 老 dws_user_reg_ltv_daily_d
```

**核心设计原则**：
1. **行级派生**：LTV 必须 (uid, amount) 配对，不能从 BITMAP 聚合表派生
   - ❌ `dws_app_user_d_h`（活跃模型，没有 amount）
   - ❌ `dws_app_order_d_h`（订单聚合表，BITMAP+SUM 后 uid+amount pair 已丢）
   - ✅ `dwd.dwd_order_paid_d`（行级充值事件，唯一可派生源）
2. **cohort 维度全部从 `dim_user_all` 取**：跟活跃模型 `dws_app_user_d_h` 和留存视图 `dws_app_retention_d_h` 口径一致，单一来源
3. **Async MV 而非普通 VIEW**：数据量虽小（30 天充值仅 77 万行），但 LTV 通常给商业 dashboard 高频查询，物化避免每次实时算
4. **每小时刷新**：跟"hourly 增量"需求对齐；MV 落后基表 ≤ 1 小时
5. **schema 完全对齐老 `dws_user_reg_ltv_daily_d`**（BIGINT new_users + DECIMAL day_0~day_30 + update_time），下游零改动

## 2. MV DDL

参 `ops_system/04.dws/dws_user_reg_ltv_d_h/dws_user_reg_ltv_d_h.sql`。

关键结构：
```sql
DROP TABLE IF EXISTS dws.dws_user_reg_ltv_d_h;

CREATE MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h
PARTITION BY dt
DISTRIBUTED BY HASH(app_code) BUCKETS 8
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)
PROPERTIES (
    "partition_refresh_number"      = "31",
    "auto_refresh_partitions_limit" = "31",
    "session.query_timeout"         = "1800"
)
AS
WITH
cohort AS ( SELECT 注册维度 FROM dim_user_all + dim_region_info_all ),
pay    AS ( SELECT uid 级 amount FROM dwd_order_paid_d 过滤 vip/coin )
SELECT
    cohort × dim × SUM(amount per day_offset) ...
FROM cohort c LEFT JOIN pay p
    ON c.app_code = p.app_code AND c.uid = p.uid
   AND p.pay_dt BETWEEN c.dt AND DATE_ADD(c.dt, INTERVAL 30 DAY)
GROUP BY c.dt, c.app_code, c.channel, c.region, c.device;
```

## 3. Schema 对齐老天表

| 字段 | 老 `dws_user_reg_ltv_daily_d` | 新 MV | 一致性 |
|---|---|---|---|
| `dt` | DATE | DATE (`DATE(dua.register_time)`) | ✅ |
| `app_code` | VARCHAR(50) | VARCHAR(50) (`dua.app_id`) | ✅ |
| `channel` | VARCHAR(64) | VARCHAR(64) (`dua.register_channel`) | ✅ |
| `region` | BIGINT | BIGINT | ✅ |
| `device` | VARCHAR(16) | VARCHAR(16) | ✅ |
| `new_users` | BIGINT | BIGINT (COUNT DISTINCT) | ✅ |
| `day_0_pay_amount` ~ `day_30_pay_amount` | DECIMAL(18,4) × 31 | DECIMAL(18,4) × 31 (SUM) | ✅ |
| `update_time` | DATETIME | DATETIME (NOW())| ✅（含义改为该 partition 最近 refresh 时刻）|

**唯一不可见差异**：老天表是 PRIMARY KEY 物理表，新版是 Async MV。下游 SELECT 完全透明。

## 4. cohort 维度从 `dim_user_all` 取

| 字段 | dim 来源 | fallback |
|---|---|---|
| `dt` | `DATE(register_time)` | NOT NULL filter |
| `app_code` | `app_id` | — |
| `channel` | `register_channel` | → `channel` → `'organic'` |
| `region` | JOIN `dim_region_info_all` ON country/province/city | `99999999` |
| `device` | `device`, 归一 | `'OTHER'` |

**为什么用 dim 而不是 dwd_user_register_d_v2**：
1. 跟活跃模型 `dws_app_user_d_h` + 留存视图 `dws_app_retention_d_h` 口径完全一致
2. dim 已经做过维度归一（register_channel 排除了 channel 漂移）
3. 单一数据源，避免三套表 channel/region/device 定义不一样
4. 老 `_d` 表用 dwd register 事件取——可能跟 dim 略有差异（dim 同步 lag），但 LTV 是天级 cohort，1 天内 lag 可接受

**风险**：dim_user_all hourly lag ~30 分钟。最新注册用户在 dim 同步前不进 cohort，导致当日 cohort 偏低。T+1 后稳定。

## 5. 刷新策略

| 配置 | 值 | 含义 |
|---|---|---|
| `REFRESH ASYNC EVERY (INTERVAL 1 HOUR)` | 1 小时 | 跟 hourly 节奏对齐 |
| `partition_refresh_number` | 31 | 每次刷新所有 31 个 partition |
| `auto_refresh_partitions_limit` | 31 | 只维护最近 31 天 partition（30 天前 cohort 窗口已关，不再刷新）|
| `session.query_timeout` | 1800 | 单次刷新最长 30 分钟 |

**为什么所有 partition 都刷**：
- 新充值事件（pay_dt = X）会更新 cohort_dt ∈ [X-30, X] 的 day_(X-cohort_dt) 字段
- 31 天 cohort 中任何 partition 都可能受新事件影响
- 增量刷新依赖 base partition → MV partition 映射；本场景 cohort_dt（来自 dim） ≠ pay_dt（dwd 分区键），SR 无法自动映射 → 全量刷新各 partition

**性能预期**（基于生产 4-26~28 数据量级估算）：
- 30 天 `dwd_order_paid_d` filter 后 = **77 万行**
- `dim_user_all` 估算几百万-千万级
- JOIN 后 GROUP BY 5 维度 = 几十万结果行
- 单次刷新预计 30 秒 - 2 分钟，hourly 跑无压力

## 6. 上线步骤

| # | 操作 | 验证 |
|---|---|---|
| 1 | 等 `dim.dim_user_all` 在生产稳定（hourly + daily 都跑通）| dim 数据完整性 |
| 2 | 执行 `dws_user_reg_ltv_d_h.sql`：drop 老 `_d_h` 物理表 + create MV | `SHOW MATERIALIZED VIEWS` |
| 3 | 触发首次刷新：`REFRESH MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h FORCE;` | 等到 `mv_status = ACTIVE` |
| 4 | 跑 §7 核查 SQL，与老 `dws.dws_user_reg_ltv_daily_d` 对账 | 见 §7.1 |
| 5 | 监控 hourly 自动刷新 24 小时 | `information_schema.task_runs` 无失败 |
| 6 | metadata 状态 `developing → online` | 元数据库 |
| 7 | 老 `dws.dws_user_reg_ltv_daily_d` 物理表评估下线（见 §8）| 下游全切到 MV 后 retire |

## 7. 数据核查规则

### 7.1 MV vs 老天表对账

```sql
-- 选 7 天 cohort 对账
WITH cohort_dates AS (
    SELECT DISTINCT dt FROM dws.dws_user_reg_ltv_daily_d
    WHERE dt >= DATE_SUB(CURDATE(), INTERVAL 31 DAY)
      AND dt <  DATE_SUB(CURDATE(), INTERVAL 24 DAY)
),
mv AS (
    SELECT dt,
        SUM(new_users)         AS nu_v,
        SUM(day_0_pay_amount)  AS d0_v,
        SUM(day_7_pay_amount)  AS d7_v,
        SUM(day_30_pay_amount) AS d30_v
    FROM dws.dws_user_reg_ltv_d_h
    WHERE dt IN (SELECT dt FROM cohort_dates)
    GROUP BY dt
),
old_table AS (
    SELECT dt,
        SUM(new_users)         AS nu_o,
        SUM(day_0_pay_amount)  AS d0_o,
        SUM(day_7_pay_amount)  AS d7_o,
        SUM(day_30_pay_amount) AS d30_o
    FROM dws.dws_user_reg_ltv_daily_d
    WHERE dt IN (SELECT dt FROM cohort_dates)
    GROUP BY dt
)
SELECT
    v.dt,
    v.nu_v, o.nu_o, (v.nu_v - o.nu_o) AS nu_diff,
    v.d0_v, o.d0_o, ROUND((v.d0_v - o.d0_o) / NULLIF(o.d0_o,0) * 100, 2) AS d0_diff_pct,
    v.d7_v, o.d7_o, ROUND((v.d7_v - o.d7_o) / NULLIF(o.d7_o,0) * 100, 2) AS d7_diff_pct,
    v.d30_v, o.d30_o, ROUND((v.d30_v - o.d30_o) / NULLIF(o.d30_o,0) * 100, 2) AS d30_diff_pct
FROM mv v JOIN old_table o ON v.dt = o.dt
ORDER BY v.dt;
-- 期望：
--   nu_diff 在 ±1% 内（cohort 取数差异：dim_user_all vs dwd_user_register_d_v2 ROW_NUMBER first-event）
--   dN_diff_pct 在 ±2% 内（amount 差异主要来自 cohort uid 集合差异）
--   完全 0 差异基本不可能（来源表不同），关注异常大的差异
```

### 7.2 守恒检查

```sql
-- new_users 必须 ≥ 1 才能有充值；day_N 不能为负
SELECT dt, app_code,
    new_users,
    day_0_pay_amount, day_7_pay_amount, day_30_pay_amount
FROM dws.dws_user_reg_ltv_d_h
WHERE dt = '2026-04-01'
  AND (new_users <= 0
       OR day_0_pay_amount < 0
       OR day_7_pay_amount < 0
       OR day_30_pay_amount < 0);
-- 期望 0 行
```

### 7.3 LTV 累计单调性（业务规律检查）

```sql
-- LTV 累计金额理论上单调递增：sum(day_0..day_N) 不会变小
-- 跟踪某 app cohort 30 天 LTV 累计曲线
SELECT dt,
    SUM(day_0_pay_amount) AS d0,
    SUM(day_0_pay_amount + day_1_pay_amount + day_2_pay_amount) AS d2_cum,
    SUM(day_0_pay_amount + day_1_pay_amount + day_2_pay_amount
        + day_3_pay_amount + day_4_pay_amount + day_5_pay_amount + day_6_pay_amount + day_7_pay_amount) AS d7_cum,
    SUM(new_users) AS new_uu
FROM dws.dws_user_reg_ltv_d_h
WHERE dt BETWEEN '2026-04-01' AND '2026-04-15'
  AND app_code = 'TJ-001'
GROUP BY dt
ORDER BY dt;
-- 期望：d2_cum >= d0, d7_cum >= d2_cum
```

### 7.4 MV 刷新状态健康检查

```sql
-- 看最近 24 次刷新是否成功
SELECT
    task_name,
    last_refresh_state,
    last_refresh_start_time,
    last_refresh_finished_time,
    last_refresh_duration AS dur_sec,
    last_refresh_error_message
FROM information_schema.materialized_views
WHERE table_name = 'dws_user_reg_ltv_d_h';

-- 看 partition 刷新历史
SELECT * FROM information_schema.task_runs
WHERE task_name LIKE '%dws_user_reg_ltv_d_h%'
ORDER BY create_time DESC LIMIT 24;
```

## 8. 老表迁移路径

| 老表 | 现状 | 处置 |
|---|---|---|
| `dws.dws_user_reg_ltv_d_h`（老 BITMAP 物理表，已设计但 hourly 跑不通）| 空表 | drop → 由本 MV 替换 |
| `dws.dws_user_reg_ltv_daily_d`（BIGINT 物理表）| online，daily 全量回刷 31 天 | 切下游到 MV → retired → drop（下游零改动）|

**切换流程**：
1. dim_user_all 在生产稳定
2. 创建 MV，首次 FORCE refresh
3. §7.1 对账 7-14 天 cohort，差异在容忍范围
4. 下游消费方逐个切换：`dws.dws_user_reg_ltv_daily_d` → `dws.dws_user_reg_ltv_d_h`
5. 全部下游切走后，drop 老 `_daily_d` 物理表

**回滚预案**：保留老 `dws_user_reg_ltv_daily_d` 调度（disabled），有问题一键 drop MV + 重启老调度回填。

## 9. 关键设计决策（review 用）

| 决策 | 选择 | 备选 | 理由 |
|---|---|---|---|
| 物化形式 | **Async MV** | 普通 VIEW / 物化表 + hourly 跨 partition INSERT INTO | LTV 给 dashboard 高频查询，物化必要；物化表 SUM 不幂等（重跑翻倍），MV 全量刷新天然幂等 |
| 派生源 | **dwd.dwd_order_paid_d** | dws_app_order_d_h | LTV 必须 (uid, amount) pair，dws 已聚合丢了 |
| cohort 来源 | **dim.dim_user_all** | dwd_user_register_d_v2（老 `_d` 用法）| 跟活跃模型 / 留存视图口径一致；dim 已做维度归一 |
| 刷新周期 | **每 1 小时** | 5 min / 1 day | 跟 hourly 节奏对齐；LTV 业务 1 小时延迟可接受 |
| 刷新范围 | **全 31 partition 每次刷** | 增量刷新（partition 映射）| 多表 JOIN MV 增量映射不可靠（cohort_dt 来自 dim ≠ pay_dt 分区键），全刷数据量小（30 秒）够快 |
| schema 列类型 | **BIGINT + DECIMAL** 对齐 `_d` | BITMAP + DECIMAL（保留 cohort BITMAP 上卷能力）| 留存视图同样选了 BIGINT；周/月 LTV 上卷需求不强，需要时另派生 |
| 时间窗口 | **30 天** | 60 / 90 / 180 天 | 跟现有 `_d` 一致；30 天后 cohort 窗口关闭，业务关注度低 |
| `update_time` | NOW() at refresh | last_refresh_time | NOW() 在 MV 里就是该 partition 最近 refresh 时刻，语义对 |

## 10. 性能与运维

### 10.1 数据量级（30 天，生产 4 月数据）

| 项 | 量级 |
|---|---|
| `dwd.dwd_order_paid_d` filter 后 | 77 万行 |
| 不同付费用户 | 68 万 |
| `dim.dim_user_all` | 千万级用户 |
| MV 输出（5 维度 GROUP）| 几十万行 |

### 10.2 单次刷新预期

- JOIN 主体：cohort × pay = 千万级 dim × 77 万 pay
- 主开销在 cohort 表 register_time NOT NULL filter（dim 全表扫）
- 预计单次刷新 30 秒 - 2 分钟

### 10.3 刷新失败兜底

```sql
-- 手动触发 force refresh（覆盖式刷新所有 partition）
REFRESH MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h FORCE;

-- 只刷指定 partition（节约成本）
REFRESH MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h
PARTITION START('2026-04-01') END('2026-04-08');

-- 暂停 / 恢复自动刷新
ALTER MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h INACTIVE;
ALTER MATERIALIZED VIEW dws.dws_user_reg_ltv_d_h ACTIVE;
```

### 10.4 监控告警建议

- `last_refresh_state = FAILED` 立即告警
- `last_refresh_duration > 1800s` 告警（接近 query_timeout）
- 当日 cohort `new_users` 远低于历史均值 告警（dim 同步 lag 异常）

## 11. 待跟进 / 决策项

1. **dim.dim_user_all 生产稳定 ETA**：MV 上线前提条件
2. **是否加 user_type 维度**：dim 有 user_type 字段，但 schema 不带（跟老 `_d` 一致）。如商业分析需要按 VIP/NORMAL 切，可后续加列
3. **老 `dws.dws_user_reg_ltv_daily_d` 何时下线**：建议 MV 上线后并行 1 个月，对账无差再 retire
4. **`dwd.dwd_order_paid_d.amount` 单位确认**：MV 假设单位是分（除 100 转元），跟老 `_d` 一致。生产投产前再核对一遍
5. **依赖一致性**：MV 依赖 `dim.dim_user_all` 字段 register_time / register_channel / device / country/province/city / uid / app_id；以及 `dwd.dwd_order_paid_d` 的 dt / app_id / uid / amount / order_type / event。任一上游改 schema 必须同步改 MV
6. **是否扩大窗口到 60/90 天**：业务方决定。窗口扩大会线性增加刷新成本，但 30 天后 cohort 窗口关闭，业务关注度通常很低

## 12. 维护约定

- MV SQL 修改 → 必须先 SELECT-only 把内层 SQL 跑一遍验证，再 DROP/CREATE MATERIALIZED VIEW（参 `feedback_etl_validation_via_select_only`）
- 跟老天表差异超过 5% → 检查 cohort 取数（dim vs dwd register）或 amount 单位换算
- per-app 核查只对**合法 app_id**（`^[A-Z]{2,3}-\d{1,4}$`）做（参 `feedback_per_app_verification_rule`）
- 上游 dim_user_all schema 变更必须同步检查本 MV 依赖的字段名
- amount 单位（分 / 元）变化必须立即跟踪修正
- MV 状态从 ACTIVE 变为 INACTIVE 必须立即排查（refresh task 失败 / 上游表不可用）
