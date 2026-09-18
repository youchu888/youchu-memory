# dws.dws_app_user_d_h 用户活跃小时模型设计 + 核查剧本

## 0. 表信息

- **目标表**：`dws.dws_app_user_d_h`
- **业务名**：用户活跃小时模型（活跃 / 新增 / 老活跃 / 设备 / 登录 5 个 BITMAP 指标）
- **业务别名**：用户活跃小时模型 / DAU 小时增量
- **业务域**：运营平台
- **状态**：developing
- **粒度**：天 partition + (app_code, channel, region, device, user_type) 6 维聚合
- **写入语义**：
  - hourly：每小时跑这一小时**事件增量**（INSERT INTO，bitmap_union 幂等）
  - daily T+1：每天 03:00 跑昨天**全天**兜底（INSERT OVERWRITE）
- **数据环境**：
  - 测试：`.claude/database/test.cnf`
  - 生产：`.claude/database/my.cnf`
- **命名约定**：当前用 `_d_h` 后缀，待稳定上线 + 旧 `dws.dws_app_user_d`（天 BIGINT）下线后再统一改名

## 1. 总览数据流

```
dwd.dwd_user_register_d_v2 ─┐                                                ┌─→ dws.dws_app_user_w  (同名视图替换原周表)
dwd.dwd_app_page_view_d    ─┼─→ dws.dws_app_user_d_h ──[BITMAP 上卷]────────┤
dwd.dwd_user_login_d_v2    ─┘   (BITMAP_UNION × 5 + AGGREGATE KEY × 6 维)    └─→ dws.dws_app_user_m  (同名视图/MV 替换原月表)

dim.dim_user_all (register_time + user_type, hourly lag ~30min)  → 新/老 + user_type 判定
dim.dim_region_info_all                                            → region 哈希
dim.dim_date_info_all (week_of_year / start_of_week / month)      → 周月时间字段对齐原表
```

**核心设计原则**：
1. 表结构 5 列 BITMAP 不动
2. hourly 跑这一小时事件增量（不跑全天，避免大表全扫）
3. **bitmap hash 用 `CONCAT(uid, '@', app_id)` 复合 hash**（本项目用户标识是 `(uid, app_id)`，不是 uid；跨 app 同 uid 是不同用户）；设备 bitmap 同样用 `CONCAT(device_id, '@', app_id)`
4. **`new_users` 和 `old_active_users` 都用 `dim.dim_user_all.register_time` 判定**：active 中 register_time >= 当日 0 点 → new；< 当日 0 点 → old。**不依赖"当时段 register 事件"**（避免漏算"早注册晚活跃"）
5. dim_user_all JOIN 用 `(uid, app_id)` 复合键，**不加 channel**（dim 是 (uid,app_id) 1:1）
6. **周 / 月用与原物理表同名的视图（或 MV）替换**：drop 原 `dws.dws_app_user_w` / `dws.dws_app_user_m`，建同名 view 从 `dws_app_user_d_h` 上卷 + JOIN `dim_date_info_all`，下游零改动
7. 守恒口径：`active = new + old`（B 方案 + 复合 hash，**严格守恒 gap=0**）

## 2. 表结构（保持现状）

```sql
CREATE TABLE IF NOT EXISTS dws.dws_app_user_d_h (
    dt               DATE         NOT NULL COMMENT "统计日期",
    app_code         VARCHAR(50)  NOT NULL COMMENT "应用唯一标识",
    channel          VARCHAR(64)  NOT NULL COMMENT "推广渠道标识",
    region           BIGINT       NOT NULL COMMENT "地理位置",
    device           VARCHAR(16)  NOT NULL COMMENT "设备类型",
    user_type        VARCHAR(50)  NOT NULL COMMENT "用户类型",

    new_users        BITMAP BITMAP_UNION COMMENT "今日新注册用户 bitmap",
    active_users     BITMAP BITMAP_UNION COMMENT "活跃用户 bitmap (DAU)",
    old_active_users BITMAP BITMAP_UNION COMMENT "老用户活跃 bitmap (register_time < 今天 0 点)",
    active_devices   BITMAP BITMAP_UNION COMMENT "活跃设备 bitmap (DAD)",
    login_users      BITMAP BITMAP_UNION COMMENT "登录用户 bitmap",

    update_time      DATETIME REPLACE COMMENT "更新时间"
)
AGGREGATE KEY(dt, app_code, channel, region, device, user_type)
PARTITION BY RANGE(dt) (START ("2025-12-20") END ("2026-05-01") EVERY (INTERVAL 1 DAY))
DISTRIBUTED BY HASH(app_code) BUCKETS 8
PROPERTIES (
    "compression" = "LZ4",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-30",
    "dynamic_partition.end"   = "7",
    "dynamic_partition.prefix" = "p",
    "replication_num" = "3"
);
```

## 3. ETL SQL（hourly 与 daily 共用模板）

```sql
-- ============================================================
-- dws.dws_app_user_d_h
-- 模式参数：
--   hourly 增量  → ${insert_mode} = INSERT INTO  + slot=[hour_start, hour_end)
--   daily 兜底   → ${insert_mode} = INSERT OVERWRITE + slot=[day_start, next_day_start)
-- ============================================================

${insert_mode} dws.dws_app_user_d_h
WITH
-- dim_user_all 不锁 row_update_time：
--   register_time 是用户首次注册时刻、immutable，不会因后续活跃 / user_type 变化而变
--   row_update_time 会随 last_active_time / user_type 等字段更新被刷新
--   如果按 row_update_time 锁快照，跨日返回的老用户会被排除（其行 row_update_time 已被推到处理日之后）→ 漏判 new/old
--   register_time 维度不需要 historical snapshot 因为它不变；user_type 维度有轻微非幂等漂移，可接受
user_dim AS (
    SELECT app_id, uid, register_time, UPPER(user_type) AS user_type
    FROM dim.dim_user_all
),

-- 本时段活跃 (page_view)
act AS (
    SELECT a.dt, a.app_id,
        COALESCE(a.channel, 'organic') AS channel,
        COALESCE(d.region, 99999999)   AS region,
        CASE WHEN UPPER(TRIM(a.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER'
             ELSE UPPER(TRIM(a.device)) END AS device,
        a.uid, a.device_id
    FROM dwd.dwd_app_page_view_d a
    LEFT JOIN dim.dim_region_info_all d
      ON a.country=d.country_name AND a.province=d.province_name AND a.city=d.city_name
    WHERE a.dt = DATE('${slot_start_time}')
      AND a.event_time >= CAST('${slot_start_time}' AS DATETIME)
      AND a.event_time <  CAST('${slot_end_time}'   AS DATETIME)
      AND a.uid IS NOT NULL AND TRIM(a.uid) <> ''
),

-- 本时段新注册
reg AS (
    SELECT r.dt, r.app_id,
        COALESCE(r.channel, 'organic') AS channel,
        COALESCE(d.region, 99999999)   AS region,
        CASE WHEN UPPER(TRIM(r.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER'
             ELSE UPPER(TRIM(r.device)) END AS device,
        r.uid, r.device_id
    FROM dwd.dwd_user_register_d_v2 r
    LEFT JOIN dim.dim_region_info_all d
      ON r.country=d.country_name AND r.province=d.province_name AND r.city=d.city_name
    WHERE r.dt = DATE('${slot_start_time}')
      AND r.event_time >= CAST('${slot_start_time}' AS DATETIME)
      AND r.event_time <  CAST('${slot_end_time}'   AS DATETIME)
      AND r.uid IS NOT NULL AND TRIM(r.uid) <> ''
),

-- 本时段登录
lg AS (
    SELECT l.dt, l.app_id,
        COALESCE(l.channel, 'organic') AS channel,
        COALESCE(d.region, 99999999)   AS region,
        CASE WHEN UPPER(TRIM(l.device)) NOT IN ('IOS','ANDROID','PC') THEN 'OTHER'
             ELSE UPPER(TRIM(l.device)) END AS device,
        l.uid, l.device_id
    FROM dwd.dwd_user_login_d_v2 l
    LEFT JOIN dim.dim_region_info_all d
      ON l.country=d.country_name AND l.province=d.province_name AND l.city=d.city_name
    WHERE l.dt = DATE('${slot_start_time}')
      AND l.event_time >= CAST('${slot_start_time}' AS DATETIME)
      AND l.event_time <  CAST('${slot_end_time}'   AS DATETIME)
      AND l.uid IS NOT NULL AND TRIM(l.uid) <> ''
),

-- 标 event 类型，3 流并轨
base AS (
    SELECT *, 'ACTIVE'   AS evt FROM act
    UNION ALL SELECT *, 'REGISTER' FROM reg
    UNION ALL SELECT *, 'LOGIN'    FROM lg
)

SELECT
    b.dt,
    b.app_id AS app_code,
    b.channel, b.region, b.device,
    COALESCE(ud.user_type, 'NORMAL') AS user_type,

    -- active_users：当时段活跃事件 ∪ 当时段新注册（注册即活跃）
    BITMAP_UNION(TO_BITMAP(
        IF(b.evt IN ('ACTIVE','REGISTER'), bitmap_hash64_udf(CONCAT(b.uid, '@', b.app_id)), NULL))) AS active_users,

    -- new_users：active 中 dim.register_time >= 当日 0 点（业务定义"今天新注册"）
    BITMAP_UNION(TO_BITMAP(
        IF(b.evt IN ('ACTIVE','REGISTER')
           AND ud.register_time IS NOT NULL
           AND ud.register_time >= DATE('${slot_start_time}'),
           bitmap_hash64_udf(CONCAT(b.uid, '@', b.app_id)), NULL))) AS new_users,

    -- old_active_users：active 中 dim.register_time < 当日 0 点 的
    BITMAP_UNION(TO_BITMAP(
        IF(b.evt IN ('ACTIVE','REGISTER')
           AND ud.register_time IS NOT NULL
           AND ud.register_time < DATE('${slot_start_time}'),
           bitmap_hash64_udf(CONCAT(b.uid, '@', b.app_id)), NULL))) AS old_active_users,

    -- active_devices：本时段活跃事件中带 device_id 的设备
    BITMAP_UNION(TO_BITMAP(
        IF(b.evt='ACTIVE' AND b.device_id IS NOT NULL AND TRIM(b.device_id)<>'',
           bitmap_hash64_udf(CONCAT(b.device_id, '@', b.app_id)), NULL))) AS active_devices,

    -- login_users：本时段登录事件 uid
    BITMAP_UNION(TO_BITMAP(
        IF(b.evt='LOGIN', bitmap_hash64_udf(CONCAT(b.uid, '@', b.app_id)), NULL))) AS login_users,

    NOW() AS update_time
FROM base b
LEFT JOIN user_dim ud
    ON b.app_id = ud.app_id AND b.uid = ud.uid       -- 不加 channel
GROUP BY
    b.dt, b.app_id, b.channel, b.region, b.device,
    COALESCE(ud.user_type, 'NORMAL');
```

**关键设计点**：
- 同一份 SQL，靠 `${insert_mode}` 切换 INSERT INTO（hourly）/ INSERT OVERWRITE（daily）
- `${slot_start_time}` / `${slot_end_time}` 是窗口；hourly 时是 1 小时、daily 时是 24 小时
- `DATE('${slot_start_time}')` = 窗口所在日的 0 点 → 用作 old/new 判定基准
- `LEFT JOIN dim.dim_user_all ON (uid, app_id)`，**不加 channel**（dim 是 (uid,app_id) 1:1，加 channel 反而漏判跨渠道活跃）
- new_users 来源：`dwd_user_register_d_v2` 当时段新注册事件
- active_users = page_view 事件 ∪ 注册事件（注册当天即活跃，对齐 dwm 旧定义）

## 4. 海豚调度配置

### 4.1 任务 1：Hourly Increment

| 项 | 值 |
|---|---|
| 节点 | SQL 节点，绑定 `dws_app_user_d_h.sql` |
| Cron | `0 30 0/1 * * ?`（每小时 30 分跑前一小时）|
| `insert_mode` | `INSERT INTO` |
| `slot_start_time` | `$[yyyy-MM-dd HH:00:00-1H]` |
| `slot_end_time` | `$[yyyy-MM-dd HH:00:00]` |

例：11:30 触发 → slot=[2026-04-29 10:00, 2026-04-29 11:00)

**理由**：上游 dwd / dim_user_all 整点 +30 分内追平，30 分跑确保数据齐了

### 4.2 任务 2：Daily T+1 Finalize

| 项 | 值 |
|---|---|
| Cron | `0 0 3 * * ?`（每天 03:00 跑昨天）|
| `insert_mode` | `INSERT OVERWRITE` |
| `slot_start_time` | `$[yyyy-MM-dd-1 00:00:00]` |
| `slot_end_time` | `$[yyyy-MM-dd 00:00:00]` |

例：2026-04-30 03:00 → slot=[2026-04-29 00:00, 2026-04-30 00:00)，OVERWRITE p20260429

**作用**：
1. OVERWRITE 清掉 hourly 累积的 segment（compaction 减压）
2. 兜底当天迟到事件（dwd 后写入的）
3. 修正 hourly 时 dim_user_all lag 漏判的 uid（dim 到 T+1 已补全 → old/new 准确）

### 4.3 任务 3：补历史数据（手工触发）

启动方式：**补数据**模式，选目标日期范围（参数同 Daily T+1）。

补 2026-04-25 → 选数据时间 = 2026-04-26（DS 解析 `$[yyyy-MM-dd-1]` = 4-25）。串行执行。

## 5. 周 / 月聚合方案（已上线，Plan B）

**核心架构**：物理 BITMAP 表增量 + 同步视图暴露 BIGINT

```
dws.dws_app_user_d_h (天 BITMAP 快照)
    ↓ daily T+1 INSERT INTO（BITMAP_UNION 自动去重，幂等）
    ├─→ dws.dws_app_user_w_d_new (周 BITMAP 物理表，AGGREGATE KEY)
    │      ↓
    │      dws.dws_app_user_w_d_view (BIGINT 视图，BITMAP_UNION_COUNT)
    │
    └─→ dws.dws_app_user_m_d_new (月 BITMAP 物理表)
           ↓
           dws.dws_app_user_m_d_view (BIGINT 视图)
```

**为什么选 Plan B（物理表 + 视图）而不是 Plan A（视图直接挂 d_h）**：
1. d_h 单天就 4M 行，跨周/跨月查询要扫 7-31 天的 BITMAP，view 实时聚合 P95 慢 5-20 倍
2. 物理表把"日 → 周/月" 的 BITMAP_UNION 提前算了一次，AGGREGATE KEY 模型自动维护去重
3. INSERT INTO + BITMAP_UNION 列**幂等**：同一天回刷多次不会膨胀（BITMAP_UNION 是集合并）
4. 月数据精确（BITMAP_UNION_COUNT），不是 HLL 近似

**ETL 文件**：
- `ops_system/04.dws/dws_app_user_w_d_new/dws_app_user_w_d_new.sql`
- `ops_system/04.dws/dws_app_user_m_d_new/dws_app_user_m_d_new.sql`

### 5.1 时间字段对齐说明

| 原表字段 | 类型 | 来源 | 视图实现 |
|---|---|---|---|
| `week` (`dws_app_user_w`) | INT (`2026018`) | `dim_date_info_all.week_of_year`（已是 `CAST(CONCAT(year, LPAD(woy,3,'0')) AS INT)`）| JOIN ddi 取 |
| `start_of_week` (`dws_app_user_w`) | DATE | `dim_date_info_all.start_of_week`（含跨年修正）| JOIN ddi 取 |
| `month` (`dws_app_user_m`) | INT (`202604`) | `dim_date_info_all.month`（已是 `CAST(CONCAT(year, LPAD(month,2,'0')) AS INT)`）| JOIN ddi 取 |

**为何走 ddi 而不是 SQL 函数现算**：跨年周（如 2025 年 12 月最后一周横跨 2026-01）口径以 ddi 为准；月维度同理。生产周/月表本身就靠 ddi，视图保持一致才能口径完全等价。

### 5.2 周物理表 + 视图 DDL —— `dws.dws_app_user_w_d_new` / `dws.dws_app_user_w_d_view`

```sql
CREATE TABLE IF NOT EXISTS dws.dws_app_user_w_d_new (
    `week`             INT          NOT NULL COMMENT "统计周（YYYY+3位周序号）",
    `start_of_week`    DATE         NOT NULL COMMENT "该周第一天",
    `app_code`         VARCHAR(50)  NOT NULL COMMENT "应用唯一标识",
    `channel`          VARCHAR(64)  NOT NULL COMMENT "推广渠道标识",
    `region`           BIGINT       NOT NULL COMMENT "地理位置 Hash 编号",
    `device`           VARCHAR(16)  NOT NULL COMMENT "设备类型",
    `user_type`        VARCHAR(50)  NOT NULL COMMENT "用户类型",

    `new_users`        BITMAP BITMAP_UNION COMMENT "当周首次注册/出现的用户 bitmap",
    `active_users`     BITMAP BITMAP_UNION COMMENT "当周启动过 App 的去重用户 bitmap",
    `old_active_users` BITMAP BITMAP_UNION COMMENT "当周老用户活跃 bitmap",
    `active_devices`   BITMAP BITMAP_UNION COMMENT "当周活跃设备 bitmap",
    `login_users`      BITMAP BITMAP_UNION COMMENT "当周登录用户 bitmap",

    `update_time`      DATETIME REPLACE COMMENT "最近一次 INSERT 时间"
)
AGGREGATE KEY(`week`, `start_of_week`, `app_code`, `channel`, `region`, `device`, `user_type`)
PARTITION BY LIST(`week`) (PARTITION p2026001 VALUES IN (('2026001')))
DISTRIBUTED BY HASH(`app_code`) BUCKETS 8
PROPERTIES ("compression"="LZ4", "replication_num"="3", "fast_schema_evolution"="true");

-- 视图：BIGINT 接口
CREATE VIEW IF NOT EXISTS dws.dws_app_user_w_d_view AS
SELECT week, app_code, channel, region, device, start_of_week, user_type,
    BITMAP_UNION_COUNT(new_users)        AS new_users,
    BITMAP_UNION_COUNT(active_users)     AS active_users,
    BITMAP_UNION_COUNT(old_active_users) AS old_active_users,
    BITMAP_UNION_COUNT(active_devices)   AS active_devices,
    BITMAP_UNION_COUNT(login_users)      AS login_users,
    MAX(update_time)                     AS update_time
FROM dws.dws_app_user_w_d_new
GROUP BY week, start_of_week, app_code, channel, region, device, user_type;
```

### 5.3 月物理表 + 视图 DDL —— `dws.dws_app_user_m_d_new` / `dws.dws_app_user_m_d_view`

```sql
CREATE TABLE IF NOT EXISTS dws.dws_app_user_m_d_new (
    `month`            INT          NOT NULL COMMENT "统计月（YYYYMM）",
    `first_of_month`   DATE         NOT NULL COMMENT "该月第一天",
    `app_code`         VARCHAR(50)  NOT NULL,
    `channel`          VARCHAR(64)  NOT NULL,
    `region`           BIGINT       NOT NULL,
    `device`           VARCHAR(16)  NOT NULL,
    `user_type`        VARCHAR(50)  NOT NULL,

    `new_users`        BITMAP BITMAP_UNION,
    `active_users`     BITMAP BITMAP_UNION,
    `old_active_users` BITMAP BITMAP_UNION,
    `active_devices`   BITMAP BITMAP_UNION,
    `login_users`      BITMAP BITMAP_UNION,

    `update_time`      DATETIME REPLACE
)
AGGREGATE KEY(`month`, `first_of_month`, `app_code`, `channel`, `region`, `device`, `user_type`)
PARTITION BY LIST(`month`) (PARTITION p202601 VALUES IN (('202601')))
DISTRIBUTED BY HASH(`app_code`) BUCKETS 8
PROPERTIES ("compression"="LZ4", "replication_num"="3", "fast_schema_evolution"="true");

CREATE VIEW IF NOT EXISTS dws.dws_app_user_m_d_view AS
SELECT month, first_of_month, app_code, channel, region, device, user_type,
    BITMAP_UNION_COUNT(new_users)        AS new_users,
    BITMAP_UNION_COUNT(active_users)     AS active_users,
    BITMAP_UNION_COUNT(old_active_users) AS old_active_users,
    BITMAP_UNION_COUNT(active_devices)   AS active_devices,
    BITMAP_UNION_COUNT(login_users)      AS login_users,
    MAX(update_time)                     AS update_time
FROM dws.dws_app_user_m_d_new
GROUP BY month, first_of_month, app_code, channel, region, device, user_type;
```

### 5.4 daily 增量 ETL（一次取一天，幂等）

**周表 ETL**（同 `ops_system/04.dws/dws_app_user_w_d_new/dws_app_user_w_d_new.sql`）：

```sql
-- step 1: 兜底新建本周 partition（LIST partition 不能 dynamic 自动加）
SELECT week_of_year FROM dim.dim_date_info_all WHERE dt = '${dt}';
ALTER TABLE dws.dws_app_user_w_d_new ADD PARTITION IF NOT EXISTS p${week_of_year} VALUES IN (('${week_of_year}'));

-- step 2: 把 d_h 当天数据 INSERT INTO，BITMAP_UNION 自动去重
INSERT INTO dws.dws_app_user_w_d_new
    (week, start_of_week, app_code, channel, region, device, user_type,
     new_users, active_users, old_active_users, active_devices, login_users, update_time)
SELECT
    ddi.week_of_year, ddi.start_of_week,
    h.app_code, h.channel, h.region, h.device, h.user_type,
    h.new_users, h.active_users, h.old_active_users, h.active_devices, h.login_users,
    NOW()
FROM dws.dws_app_user_d_h h
JOIN dim.dim_date_info_all ddi ON ddi.dt = h.dt
WHERE h.dt = '${dt}';
```

**月表 ETL**（同 `ops_system/04.dws/dws_app_user_m_d_new/dws_app_user_m_d_new.sql`）：

```sql
SELECT month FROM dim.dim_date_info_all WHERE dt = '${dt}';
ALTER TABLE dws.dws_app_user_m_d_new ADD PARTITION IF NOT EXISTS p${month} VALUES IN (('${month}'));

INSERT INTO dws.dws_app_user_m_d_new
    (month, first_of_month, app_code, channel, region, device, user_type,
     new_users, active_users, old_active_users, active_devices, login_users, update_time)
SELECT
    ddi.month, DATE_TRUNC('month', ddi.dt),
    h.app_code, h.channel, h.region, h.device, h.user_type,
    h.new_users, h.active_users, h.old_active_users, h.active_devices, h.login_users,
    NOW()
FROM dws.dws_app_user_d_h h
JOIN dim.dim_date_info_all ddi ON ddi.dt = h.dt
WHERE h.dt = '${dt}';
```

**为什么不会膨胀**：AGGREGATE KEY + BITMAP_UNION 列在同一组 KEY 上多次 INSERT，引擎自动 BITMAP_UNION（集合并），重复跑某天**只会刷新 update_time**，BITMAP 不会变。

### 5.5 海豚调度配置（daily T+1）

| 项 | 周表任务 | 月表任务 |
|---|---|---|
| 节点 | SQL 节点，绑定 `dws_app_user_w_d_new.sql` | SQL 节点，绑定 `dws_app_user_m_d_new.sql` |
| Cron | `0 30 3 * * ?`（每天 03:30，d_h T+1 之后）| `0 30 3 * * ?` 同上 |
| 参数 | `dt = $[yyyy-MM-dd-1]` | `dt = $[yyyy-MM-dd-1]` |
| 依赖 | dws_app_user_d_h daily T+1（§4.2）成功 | 同左 |

**调度顺序**：`d_h daily T+1 (03:00) → w_d_new (03:30) → m_d_new (03:30)`（周月并行，互不影响）

### 5.6 历史回刷流程

**用海豚补数据（推荐）**：

1. 海豚 → 工作流定义 → 周/月任务 → 选"补数据"
2. 数据时间范围：起点 = 最早未刷日期 + 1（因为 `${dt}=$[yyyy-MM-dd-1]`），终点 = 今天
3. 调度方式：串行
4. 失败重试：3 次

**手工 SQL 循环**（如果海豚不便用）：

```bash
# 用 mysql 客户端循环跑 daily ETL
for d in $(seq 0 30); do
  DT=$(date -j -v-${d}d -f "%Y-%m-%d" "2026-04-30" "+%Y-%m-%d" 2>/dev/null \
        || date -d "2026-04-30 -${d} day" "+%Y-%m-%d")  # macOS / linux 兼容

  echo ">>> backfill dt=$DT"
  WEEK=$(mysql --defaults-extra-file=.claude/database/my.cnf -N -B -e "SELECT week_of_year FROM dim.dim_date_info_all WHERE dt='$DT'")
  MONTH=$(mysql --defaults-extra-file=.claude/database/my.cnf -N -B -e "SELECT \`month\` FROM dim.dim_date_info_all WHERE dt='$DT'")

  mysql --defaults-extra-file=.claude/database/my.cnf -e "
    ALTER TABLE dws.dws_app_user_w_d_new ADD PARTITION IF NOT EXISTS p${WEEK} VALUES IN (('${WEEK}'));
    INSERT INTO dws.dws_app_user_w_d_new
      (week, start_of_week, app_code, channel, region, device, user_type,
       new_users, active_users, old_active_users, active_devices, login_users, update_time)
    SELECT ddi.week_of_year, ddi.start_of_week,
           h.app_code, h.channel, h.region, h.device, h.user_type,
           h.new_users, h.active_users, h.old_active_users, h.active_devices, h.login_users,
           NOW()
    FROM dws.dws_app_user_d_h h JOIN dim.dim_date_info_all ddi ON ddi.dt = h.dt
    WHERE h.dt = '$DT';

    ALTER TABLE dws.dws_app_user_m_d_new ADD PARTITION IF NOT EXISTS p${MONTH} VALUES IN (('${MONTH}'));
    INSERT INTO dws.dws_app_user_m_d_new
      (month, first_of_month, app_code, channel, region, device, user_type,
       new_users, active_users, old_active_users, active_devices, login_users, update_time)
    SELECT ddi.\`month\`, DATE_TRUNC('month', ddi.dt),
           h.app_code, h.channel, h.region, h.device, h.user_type,
           h.new_users, h.active_users, h.old_active_users, h.active_devices, h.login_users,
           NOW()
    FROM dws.dws_app_user_d_h h JOIN dim.dim_date_info_all ddi ON ddi.dt = h.dt
    WHERE h.dt = '$DT';
  "
done
```

**回刷幂等保证**：BITMAP_UNION 是集合并，同一 (week, dim) 多次写只是 union 同一份 BITMAP，结果不变；update_time 会刷成最新，便于追溯。

### 5.7 与老表 / Plan A 的差异

| 项 | 老 BIGINT 物理表 (dws_app_user_w / _m) | Plan A：视图直接挂 d_h | **Plan B（已上线）** |
|---|---|---|---|
| 周表去重 | `COUNT(DISTINCT uid)` 精确 | BITMAP_UNION_COUNT 精确（跨 7 天 union d_h）| BITMAP_UNION_COUNT 精确（已预聚合）|
| 月表去重 | HLL 近似（误差 1-2%）| BITMAP_UNION_COUNT 精确 | BITMAP_UNION_COUNT **精确** |
| 写入语义 | T+1 整周 / 整月 INSERT OVERWRITE | 视图无写入 | T+1 daily INSERT INTO（幂等）|
| 查询性能 | 物理表预聚合，扫描成本最低 | view 实时上卷 d_h，慢 5-20× | 物理表预聚合，跟老表同档 |
| 全量回刷 | 重跑整周 / 整月 SQL | 无回刷概念 | 循环跑 31 个 daily 增量 |
| 数据可见性 | T+1 整周才有数据 | 跟天表同步 | T+1 daily 跑完即可见 |
| `update_time` | 调度落库时间 | NOW() 查询时间 | REPLACE 列，每行最近一次 INSERT |

### 5.8 视图核查记录

| 项 | 老表 | 新视图 | 影响 |
|---|---|---|---|
| 周表去重 | `COUNT(DISTINCT uid)` 精确 | BITMAP_UNION_COUNT 精确 | **数字一致** |
| 月表去重 | `hll_union_agg` **近似**（误差 ~1-2%）| BITMAP_UNION_COUNT **精确** | **数字会变准**（视为改进，需提前打招呼）|
| `update_time` | 调度落库时间，每行固定 | `NOW()` 查询时间 | 如下游依赖此值排序请改用别的字段 |
| 全表扫性能 | 物理表预聚合，扫描成本低 | 实时上卷天表 BITMAP，单查询慢 5-20 倍 | 见 §5.5 |
| 写入延迟 | T+1 整周 / 整月跑完才有数据 | 跟天表同步，T+1 后整周/月可查 | 数据可见性提升 |

**核查 1：跨维度 BIGINT 总和（含伪重复 SUM）**

| 来源 | new | active | old_active | active_devices | login |
|---|---:|---:|---:|---:|---:|
| d_h 4-29 SUM(BITMAP_COUNT) | 4,175,557 | 14,700,456 | 10,524,899 | 16,902,012 | 11,427,265 |
| 周视图 W18 SUM(BIGINT) | 4,175,557 | 14,700,456 | 10,524,899 | 16,902,012 | 11,427,265 |
| 月视图 04 SUM(BIGINT) | 4,175,557 | 14,700,456 | 10,524,899 | 16,902,012 | 11,427,265 |

**✅ 三层完全相等**

**核查 2：跨所有维度真去重**

| 来源 | new | active | old_active | active_devices | login |
|---|---:|---:|---:|---:|---:|
| d_h 4-29 BITMAP_UNION_COUNT | 3,693,293 | 13,155,299 | 9,462,006 | 15,180,942 | 11,047,792 |
| 周物理表 W18 BITMAP_UNION_COUNT | 3,693,293 | 13,155,299 | 9,462,006 | 15,180,942 | 11,047,792 |
| 月物理表 04 BITMAP_UNION_COUNT | 3,693,293 | 13,155,299 | 9,462,006 | 15,180,942 | 11,047,792 |

**✅ 三层 BITMAP 真去重数完全相等**

**核查 3：头部 5 维度组合行级抽样**——三层 active / new / login 三指标全 0 diff（详见验证记录文档）。

**核查 4：与 dwd 源对账**

| 指标 | 视图侧 distinct | dwd 源 distinct(4-29) | 差值 | 解读 |
|---|---:|---:|---:|---|
| login_users | 11,047,792 | 11,047,792（dwd_user_login_d_v2） | **0** | ✅ 完全一致 |
| new_users | 3,693,293 | 3,879,205（dwd_user_register_d_v2） | -185,912 | ✅ 视图小是对的——`new_users` 定义是 active ∩ register_today |
| active_users | 13,155,299 | 11,320,249（dwd_app_page_view_d） | +1,835,050 | ✅ 视图大是对的——active = page_view ∪ register |

**结论**：视图数据正确，d_h → 周 / 月 BITMAP 物理表 → 视图四层完全一致。

**已知现状（2026-04-30 时点）**：
- 周月物理表只 ingest 了 4-29 一天数据
- 历史 d_h 03-31 ~ 04-28 + 04-30 共 30 天**待回刷**（用 §5.6 流程）

### 5.9 性能升级路径（view → MV）

如果未来观察到周/月 view 查询慢（业务月报场景），可以再叠一层物化视图：

```sql
-- 月物理表上叠 MV，view 切换指向 MV
DROP VIEW dws.dws_app_user_m_d_view;
CREATE MATERIALIZED VIEW dws.dws_app_user_m_d_mv
DISTRIBUTED BY HASH(app_code) BUCKETS 8
REFRESH ASYNC START('2026-05-01 04:30:00') EVERY (INTERVAL 1 DAY)
PROPERTIES ("replication_num"="3")
AS
SELECT month, first_of_month, app_code, channel, region, device, user_type,
    BITMAP_UNION_COUNT(new_users)        AS new_users,
    BITMAP_UNION_COUNT(active_users)     AS active_users,
    BITMAP_UNION_COUNT(old_active_users) AS old_active_users,
    BITMAP_UNION_COUNT(active_devices)   AS active_devices,
    BITMAP_UNION_COUNT(login_users)      AS login_users,
    MAX(update_time)                     AS update_time
FROM dws.dws_app_user_m_d_new
GROUP BY month, first_of_month, app_code, channel, region, device, user_type;

CREATE VIEW dws.dws_app_user_m_d_view AS SELECT * FROM dws.dws_app_user_m_d_mv;
```

下游报表语义不变；MV 自动 daily 刷新。当前默认不上 MV，月查询 P95 > 5s 再升级。

## 6. 业务查询样例

### 6.1 当日实时（直接查天表）

```sql
SELECT app_code,
       BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_users)) AS dau,
       BITMAP_UNION_COUNT(BITMAP_UNION_AGG(new_users))    AS new_count,
       BITMAP_UNION_COUNT(BITMAP_UNION_AGG(login_users))  AS login_count
FROM dws.dws_app_user_d_h
WHERE dt = '2026-04-29'
GROUP BY app_code;
```

### 6.2 周报（如建了 MV，自动路由）

```sql
-- 写法 1：直接查 MV
SELECT week_start, app_code,
       BITMAP_UNION_COUNT(active_users) AS wau
FROM dws.mv_app_user_w
WHERE week_start = '2026-04-21'
GROUP BY week_start, app_code;

-- 写法 2：查天表，SR 优化器自动路由到 MV（GROUP BY 表达式跟 MV 一致时）
SELECT DATE_SUB(dt, INTERVAL WEEKDAY(dt) DAY) AS week_start, app_code,
       BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_users)) AS wau
FROM dws.dws_app_user_d_h
WHERE dt BETWEEN '2026-04-21' AND '2026-04-27'
GROUP BY DATE_SUB(dt, INTERVAL WEEKDAY(dt) DAY), app_code;
```

### 6.3 hourly 当日 T+1 之前旁路算 old_active

```sql
-- 当日 hourly 阶段，old_active_users 是渐进的（dim lag 影响）
-- 业务消费方需要"准实时"老活跃可用 BITMAP_AND_NOT 当场算
SELECT app_code,
       BITMAP_UNION_COUNT(BITMAP_AND_NOT(
           BITMAP_UNION_AGG(active_users),
           BITMAP_UNION_AGG(new_users))) AS old_active_realtime
FROM dws.dws_app_user_d_h
WHERE dt = CURDATE()
GROUP BY app_code;
-- T+1 finalize 后 → 直接 BITMAP_UNION_COUNT(old_active_users)
```

## 7. 数据核查规则

### 7.1 hourly 跑完观察（动态累积）

```sql
-- 当日 dws total vs dwd 上游 distinct uid
WITH dws_today AS (
  SELECT
    BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_users))   AS dws_active,
    BITMAP_UNION_COUNT(BITMAP_UNION_AGG(new_users))      AS dws_new,
    BITMAP_UNION_COUNT(BITMAP_UNION_AGG(login_users))    AS dws_login,
    BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_devices)) AS dws_dev
  FROM dws.dws_app_user_d_h WHERE dt = CURDATE()
),
dwd_today AS (
  SELECT
    (SELECT COUNT(DISTINCT uid) FROM dwd.dwd_app_page_view_d
     WHERE dt = CURDATE() AND uid IS NOT NULL AND TRIM(uid)<>'') AS dwd_active,
    (SELECT COUNT(DISTINCT uid) FROM dwd.dwd_user_register_d_v2
     WHERE dt = CURDATE() AND uid IS NOT NULL AND TRIM(uid)<>'') AS dwd_new,
    (SELECT COUNT(DISTINCT uid) FROM dwd.dwd_user_login_d_v2
     WHERE dt = CURDATE() AND uid IS NOT NULL AND TRIM(uid)<>'') AS dwd_login,
    (SELECT COUNT(DISTINCT device_id) FROM dwd.dwd_app_page_view_d
     WHERE dt = CURDATE() AND device_id IS NOT NULL AND TRIM(device_id)<>'') AS dwd_dev
)
SELECT * FROM dws_today, dwd_today;
-- 期望差距 < 1%（dim_user_all hourly lag + 跨小时 1 小时窗口偏差）
```

### 7.2 T+1 finalize 后核查（守恒 + 跨维度）

```sql
-- 1. 守恒：active = (new ∪ old) + (dim 漏的 uid)
WITH agg AS (
  SELECT
    BITMAP_UNION_AGG(active_users)     AS au,
    BITMAP_UNION_AGG(new_users)        AS nu,
    BITMAP_UNION_AGG(old_active_users) AS ou
  FROM dws.dws_app_user_d_h WHERE dt='2026-04-28'
)
SELECT
  BITMAP_UNION_COUNT(au)                              AS active_uu,
  BITMAP_UNION_COUNT(BITMAP_OR(nu, ou))               AS new_or_old_uu,
  BITMAP_UNION_COUNT(BITMAP_AND_NOT(au, BITMAP_OR(nu, ou))) AS dim_unknown,  -- dim 漏的（理想 → 0）
  BITMAP_UNION_COUNT(BITMAP_AND(nu, ou))              AS overlap             -- 应严格 = 0
FROM agg;

-- 2. per-app 拆分（仅合法 app_id）
SELECT app_code,
  BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_users))     AS dau,
  BITMAP_UNION_COUNT(BITMAP_UNION_AGG(new_users))        AS new_uu,
  BITMAP_UNION_COUNT(BITMAP_UNION_AGG(old_active_users)) AS old_uu,
  BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_devices))   AS dev_uu,
  BITMAP_UNION_COUNT(BITMAP_UNION_AGG(login_users))      AS login_uu
FROM dws.dws_app_user_d_h
WHERE dt='2026-04-28' AND app_code REGEXP '^[A-Z]{2,3}-[0-9]{1,4}$'
GROUP BY app_code ORDER BY dau DESC LIMIT 20;
```

### 7.3 周 / 月 MV 跟天表上卷对账（建 MV 后跑）

```sql
WITH from_mv AS (
  SELECT app_code, BITMAP_UNION_COUNT(active_users) AS wau
  FROM dws.mv_app_user_w WHERE week_start='2026-04-21'
  GROUP BY app_code
),
from_dh AS (
  SELECT app_code, BITMAP_UNION_COUNT(BITMAP_UNION_AGG(active_users)) AS wau
  FROM dws.dws_app_user_d_h
  WHERE dt BETWEEN '2026-04-21' AND '2026-04-27'
  GROUP BY app_code
)
SELECT m.app_code, m.wau mv_wau, d.wau dh_wau, (m.wau - d.wau) diff
FROM from_mv m JOIN from_dh d USING(app_code)
WHERE m.wau != d.wau;
-- 期望 0 行
```

## 8. 上线步骤

| # | 操作 | 验证 |
|---|---|---|
| 1 | 部署 ETL SQL（仓库 ops_system 落档） | git diff |
| 2 | 海豚配置 hourly + daily 任务，**先关闭调度** | 任务定义存在 |
| 3 | **手工触发一次 daily T+1**（slot=昨天 0~今天 0），跑 1 个 partition | 跑出数据 |
| 4 | §7.2 核查 SQL，跟旧 dwm 数据对账（差距 < 1%） | 不达标 → 修 ETL 后回到 #3 |
| 5 | 启动 hourly 调度，观察 24 小时 segment 不爆 | hourly run < 30s |
| 6 | 启动 daily T+1 调度 | T+1 03:00 自动 OVERWRITE |
| 7 | metadata 状态 `developing → online` | 元数据库 |
| 8 | （可选，观察 1-2 周后）部署周/月 MV | `SHOW MATERIALIZED VIEWS` |
| 9 | （可选）跑 §7.3 MV 对账 | 0 差异 |
| 10 | （后续）老表迁移（见 §9） | |

## 9. 老表迁移路径

| 老表 | 现状 | 处置 | 切换方式 |
|---|---|---|---|
| `dws.dws_app_user_d` | online，BIGINT 天表 | retired → drop | 下游全切 `_d_h` + BITMAP_UNION_COUNT 后 → 与 `_d_h` 命名最终化（见 §11.4）|
| `dws.dws_app_user_w` | online，BIGINT 周表 | drop 物理表 → **建同名视图**（§5.2）| 下游 SELECT 零改动 |
| `dws.dws_app_user_m` | online，BIGINT 月表 | drop 物理表 → **建同名视图**（§5.3）| 同上；月数从 HLL 近似变精确，需提前知会 |
| `dwm.dwm_app_user_d` | retired，原 dws 旧版上游 | 新 dws 不再依赖；如无别下游则 drop | — |

**切换流程（推荐）**：
1. `_d_h` 跑稳 1-2 周，§7.2 核查 gap=0
2. 跟新视图并行核对 7 天（同 dt 周/月数 vs 老表）：周一致 / 月差距应在 HLL 误差区间内
3. drop 老周/月表 → CREATE VIEW 同名视图（同一事务窗口内完成，避免下游断流）
4. 观察 1 周下游报表无异常 → 关闭老周/月调度任务

**回滚预案**：保留老 ETL 脚本和老调度任务（disabled 状态），如视图性能不达标可一键 drop view + 恢复老表 + 重启调度回填。

## 10. 关键设计决策（review 用）

| 决策 | 选择 | 备选 | 理由 |
|---|---|---|---|
| old/new 判定源 | **dim.register_time** | 今日 register cohort | dim 稳定，跨小时一致；register cohort 跨小时存在 new/old 重叠风险 |
| dim_user_all JOIN 维度 | **(uid, app_id)** | (uid, app_id, channel) | dim 是 (uid,app_id) 1:1；加 channel 漏判跨渠道活跃 |
| hourly 是否写 old_active_users | **写**（用 dim） | 不写、T+1 兜 | dim 让 hourly 就能算对，不用等 T+1 |
| new_users 来源 | **dim.register_time >= today 的 active uid** | dwd_user_register_d_v2 当时段事件 | 业务定义"今天新注册"=今天 register_time 的用户；事件源会漏"早注册晚活跃"21K（3% gap）；用 dim 守恒近完美 |
| 周 / 月模型 | **同名视图直接替换原物理表** | 独立 MV / 保留老 BIGINT 表 | 下游 SELECT 零改动，时间字段走 `dim_date_info_all` JOIN 跟原表完全一致；月去重从 HLL 升级为精确 BITMAP |
| 视图 vs MV | **先 view，慢了再升 MV** | 上线就 MV | view 实现简单、零维护；性能不达标再升级（§5.5）|
| hourly 写入语义 | **INSERT INTO + bitmap_union 幂等** | INSERT OVERWRITE 全天每次重写 | 避免大表全扫；OVERWRITE 留给 T+1 |
| daily T+1 写入语义 | **INSERT OVERWRITE** | INSERT INTO 兜底 | 清 hourly segment + 兜迟到事件 |

## 10.1 设计验证（2026-04-29 SELECT-only 测试）

### 最终方案三轮测试均 gap = 0 ✅

| 测试场景 | rows | active | new | old | gap |
|---|---|---|---|---|---|
| Daily 全天 [2026-04-28] | 4,112,501 | 12,996,122 | 3,865,610 | 9,130,512 | **0** ✅ |
| Hourly [2026-04-29 12:00, 13:00) | 503,276 | 698,046 | 160,406 | 537,640 | **0** ✅ |
| Per-app top 15 (4-28 daily) | — | 各 app 独立 | — | — | **15/15 全 0** ✅ |

### Per-app 数据合理性抽查

| app | active | new | old | 解读 |
|---|---|---|---|---|
| SF-99 | 264,872 | 264,872 (100%) | 0 | 当天纯新 app |
| TJ-001 | 1,964,120 | 815 (0.04%) | 1,963,305 | 极成熟 app |
| DX-079 | 143,412 | 133,911 (93%) | 9,501 | 新发布扩量期 |
| HX-001 | 483,147 | 147,136 (30%) | 336,011 | 健康新老比 |

### 设计修正历史（共 3 处 bug 通过迭代测试发现）

| # | 起初设计 | 测试发现 | 修法 |
|---|---|---|---|
| 1 | new_users 来源 = `dwd_user_register_d_v2` 当时段事件 | hourly 测试 gap +3.0%：漏算"早注册晚活跃"21K 用户 | 改用 `dim.register_time` 判定 new |
| 2 | bitmap hash = `bitmap_hash64_udf(uid)` | daily 测试 gap -0.85%：跨 app 同 uid 在 new+old 双计 107K | 改复合 hash `CONCAT(uid, '@', app_id)` |
| 3 | `WHERE row_update_time <= slot_end_time + 1h` | daily 测试 gap +5.58%：跨日返回的老用户 row_update_time 被推到当前日，被 buffer 排除 | **不锁** row_update_time（register_time 是 immutable，不需要 historical snapshot）|

最终方案（剧本 §3）：
- new / old / active / device / login 全部用 `bitmap_hash64_udf(CONCAT(uid_or_dev, '@', app_id))` 复合 hash
- new = active ∩ `dim.register_time >= today_0am`；old = active ∩ `dim.register_time < today_0am`
- dim_user_all JOIN ON (uid, app_id) 不锁 row_update_time

## 11. 待跟进 / 决策项

1. **周/月视图 → MV 升级时机**：默认 view 上线，月报 P95 > 5s 时升级为 MV+view 两层（§5.5）。需要监控查询耗时
2. **dws.dws_app_user_d / _w / _m 老表下线节奏**：等 `_d_h` 稳定多久才开始切？建议至少 2 周对账无差再启动迁移
3. **月数从近似变精确的下游沟通**：老 `dws_app_user_m` 用 HLL 近似（误差 1-2%），新视图精确。切换前需提前知会下游报表方，避免被当做"数据异常"
4. **dwm.dwm_app_user_d 是否同步下线**：新 dws 不再依赖；先扫下游消费方，全部切走后 retired
5. **命名最终化**：稳定后是否把 `dws_app_user_d_h` 改名为 `dws_app_user_d`（统一命名）？建议：先观察周期内保持 `_d_h`，对账完成 + 老 `_d` drop 后再做 rename

## 12. 维护约定

- ETL SQL 修改 → 必须先 SELECT-only 验证再改 INSERT 部分（参 `feedback_etl_validation_via_select_only`）
- dim.register_time 计算依据变化 → 需更新本剧本 §3 + §10 决策表
- 新增维度（如 user_type 增加新值、device 增加新分类）→ 需检查 ETL 标准化逻辑是否覆盖
- per-app 核查只对**合法 app_id**（`^[A-Z]{2,3}-\d{1,4}$`）做（参 `feedback_per_app_verification_rule`）
- hourly + daily 双调度 + 补数据 ad-hoc 三个入口必须**互不冲突**（dt 不同 partition；同一 partition 不应被多个任务并发写）
