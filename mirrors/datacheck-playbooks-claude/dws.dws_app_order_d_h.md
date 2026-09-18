# dws.dws_app_order_d_h 订单模型小时模型设计 + 核查剧本

## 0. 表信息

- **目标表**：`dws.dws_app_order_d_h`
- **业务名**：订单模型小时表（创建 / 支付 / 新老用户支付 共 12 个金额-计数指标 + BITMAP 去重用户）
- **业务别名**：订单模型小时表 / 订单聚合小时表
- **业务域**：运营平台
- **状态**：developing
- **粒度**：天 partition + 7 维聚合 `(dt, app_code, channel, region, device, order_type, user_type)`
- **金额单位**：**分**（与 `dwd.dwd_order_paid_d` 源、`dws.dws_app_order_d` 老天表、`dws.dws_user_promotion_behavior_*` 等所有项目内 dws 金额表保持一致）
- **写入语义**：
  - hourly：每小时 OVERWRITE 当天 partition，从 0:00 累积到当前整点
  - daily T+1：03:00 OVERWRITE 前一天 partition，完整 [00:00, 24:00) 兜底
- **绑定程序**：`/ops_system/04.dws/dws_app_order_d_h/dws_app_order_d_h.sql`

## 1. 总览数据流

```
dwd.dwd_order_created_h ─┐                                    ┌─→ ads.* 订单看板（待迁移）
dwd.dwd_order_paid_d    ─┼─→ dws.dws_app_order_d_h ──────────┤
dwd.dwd_user_register_d_v2 ─┘ (BITMAP_UNION × 3 + BIGINT SUM × 4 + DECIMAL SUM × 4)

dim.dim_user_all (user_type)        → user_type 维度
dim.dim_region_info_all              → region 哈希
dwd.dwd_user_register_d_v2 当天注册   → new / old 拆分判定
```

**核心设计原则**：
1. 12 个 BIGINT/DECIMAL 指标可直接 SUM；3 个 BITMAP 用 BITMAP_UNION_COUNT 取 distinct uid
2. **金额单位统一为分**（与 dwd 源、其他 dws 表口径一致）；下游需要元自行 `/ 100`
3. **new vs old 用"当天 dwd 注册事件"判定**：付费 uid 在当天 register 流里 → new；不在 → old
4. user_type / device 维度兜底：dim 没记录默认 `NORMAL` / `OTHER`
5. hourly OVERWRITE 整 partition：每小时累积当天 0:00 到当前整点（**非增量 INSERT INTO**），跑完即覆盖
6. daily T+1 OVERWRITE 兜底：完整 24 小时窗 + dim 已稳定，兜迟到事件 + 修 hourly 用 dim 的时点漂移

## 2. 表结构（生产现状）

```sql
CREATE TABLE IF NOT EXISTS dws.dws_app_order_d_h (
    `dt`                  DATE          NOT NULL COMMENT "统计日期",
    `app_code`            VARCHAR(32)   NOT NULL COMMENT "应用唯一标识",
    `channel`             VARCHAR(50)   NOT NULL COMMENT "推广渠道标识",
    `region`              BIGINT        NOT NULL COMMENT "地理位置 Hash",
    `device`              VARCHAR(16)   NOT NULL COMMENT "终端设备类型",
    `order_type`          VARCHAR(16)   NOT NULL COMMENT "订单类型: coin_purchase / vip_subscription",
    `user_type`           VARCHAR(16)   NOT NULL COMMENT "用户类型: VIP / NORMAL",

    `order_create_users`  BITMAP BITMAP_UNION COMMENT "意向用户 bitmap（uid 去重）",
    `order_create_cnt`    BIGINT SUM DEFAULT "0" COMMENT "意向订单总数",
    `order_create_amt`    DECIMAL(38,4) SUM DEFAULT "0" COMMENT "意向订单总金额（分）",

    `order_pay_users`     BITMAP BITMAP_UNION COMMENT "付款用户 bitmap",
    `order_pay_cnt`       BIGINT SUM DEFAULT "0" COMMENT "付款订单总数",
    `order_pay_amt`       DECIMAL(38,4) SUM DEFAULT "0" COMMENT "实际入账金额（分）",

    `new_order_pay_users` BITMAP BITMAP_UNION COMMENT "新用户付款 bitmap",
    `new_order_pay_cnt`   BIGINT SUM DEFAULT "0" COMMENT "新用户付款订单数",
    `new_order_pay_amt`   DECIMAL(38,4) SUM DEFAULT "0" COMMENT "新用户付款金额（分）",

    `old_order_pay_users` BITMAP BITMAP_UNION COMMENT "老用户付款 bitmap",
    `old_order_pay_cnt`   BIGINT SUM DEFAULT "0" COMMENT "老用户付款订单数",
    `old_order_pay_amt`   DECIMAL(38,4) SUM DEFAULT "0" COMMENT "老用户付款金额（分）",

    `update_time`         DATETIME REPLACE COMMENT "最近一次 INSERT 时间"
)
AGGREGATE KEY(`dt`, `app_code`, `channel`, `region`, `device`, `order_type`, `user_type`)
PARTITION BY RANGE(`dt`)(START ("2025-12-20") END ("2026-05-01") EVERY (INTERVAL 1 DAY))
DISTRIBUTED BY HASH(`app_code`) BUCKETS 16
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

> 注意：metadata.db 里 `*_cnt` 字段类型标的是 BITMAP，**生产实际是 BIGINT SUM**——元数据采集时的列类型识别有 bug，待修复（不影响业务，只影响 metadata UI 展示）。

## 3. ETL SQL（hourly 与 daily 共用模板）

```sql
-- ============================================================
-- dws.dws_app_order_d_h
-- 写入语义：INSERT OVERWRITE 整 partition（不是 INSERT INTO 增量）
-- 模式参数：
--   hourly  → PARTITION ('p$[yyyyMMdd-1H/yyyyMMdd]')
--             slot_start_time = $[yyyy-MM-dd-1H/yyyy-MM-dd 00:00:00]
--             slot_end_time   = $[yyyy-MM-dd HH:00:00]
--   daily   → PARTITION ('p$[yyyyMMdd-1]')
--             slot_start_time = $[yyyy-MM-dd 00:00:00-1]
--             slot_end_time   = $[yyyy-MM-dd 00:00:00]
-- 金额单位：分（dwd 源是分，本表保持分；下游需要元自行 / 100）
-- ============================================================

INSERT OVERWRITE dws.dws_app_order_d_h PARTITION (...)
WITH user_type_info AS (
    SELECT uid, app_id, channel, UPPER(user_type) AS user_type
    FROM dim.dim_user_all
    WHERE row_update_time <= CAST('${slot_end_time}' AS DATETIME)
),
user_registration AS (
    -- 当天注册事件，用于 new / old 拆分（uid 在则 new，不在则 old）
    SELECT DISTINCT uid, app_id, channel
    FROM dwd.dwd_user_register_d_v2
    WHERE dt = DATE('${slot_start_time}')
      AND event_time <= CAST('${slot_end_time}' AS DATETIME)
),
order_created AS (
    SELECT r.dt, r.app_id,
        COALESCE(r.channel, 'organic')                          AS channel,
        COALESCE(d.region, 99999999)                            AS region,
        CASE WHEN UPPER(TRIM(r.device)) NOT IN ('IOS','ANDROID','PC')
             THEN 'OTHER' ELSE UPPER(TRIM(r.device)) END        AS device,
        r.order_type,
        COALESCE(ut.user_type, 'NORMAL')                        AS user_type,
        BITMAP_UNION(TO_BITMAP(bitmap_hash64_udf(r.uid)))       AS order_create_users,
        COUNT(DISTINCT r.event_id)                              AS order_create_cnt,
        -- 单位 = 分
        SUM(CAST(r.amount AS DECIMAL(18,4)))                    AS order_create_amt
    FROM dwd.dwd_order_created_h r
    LEFT JOIN dim.dim_region_info_all d
      ON r.country=d.country_name AND r.province=d.province_name AND r.city=d.city_name
    LEFT JOIN user_type_info ut
      ON r.uid=ut.uid AND r.app_id=ut.app_id AND r.channel=ut.channel
    WHERE r.dt = DATE('${slot_start_time}')
      AND r.event_time <= CAST('${slot_end_time}' AS DATETIME)
      AND r.order_type IN ('coin_purchase', 'vip_subscription')
      AND r.uid IS NOT NULL AND r.event_id IS NOT NULL
    GROUP BY r.dt, r.app_id, COALESCE(r.channel, 'organic'),
             COALESCE(d.region, 99999999),
             CASE WHEN UPPER(TRIM(r.device)) NOT IN ('IOS','ANDROID','PC')
                  THEN 'OTHER' ELSE UPPER(TRIM(r.device)) END,
             r.order_type, COALESCE(ut.user_type, 'NORMAL')
),
order_paid AS (
    SELECT r.dt, r.app_id, /* 维度同上 */ ...,
        BITMAP_UNION(TO_BITMAP(bitmap_hash64_udf(r.uid)))                    AS order_pay_users,
        COUNT(DISTINCT r.event_id)                                            AS order_pay_cnt,
        SUM(CAST(r.amount AS DECIMAL(18,4)))                                  AS order_pay_amt,

        -- new = 当天 register 流命中
        BITMAP_UNION(TO_BITMAP(CASE WHEN ur.uid IS NOT NULL
                                    THEN bitmap_hash64_udf(r.uid) END))      AS new_order_pay_users,
        COUNT(DISTINCT CASE WHEN ur.uid IS NOT NULL THEN r.event_id END)     AS new_order_pay_cnt,
        SUM(CASE WHEN ur.uid IS NOT NULL THEN CAST(r.amount AS DECIMAL(18,4))
                 ELSE 0 END)                                                  AS new_order_pay_amt,

        -- old = 当天 register 流未命中
        BITMAP_UNION(TO_BITMAP(CASE WHEN ur.uid IS NULL
                                    THEN bitmap_hash64_udf(r.uid) END))      AS old_order_pay_users,
        COUNT(DISTINCT CASE WHEN ur.uid IS NULL THEN r.event_id END)         AS old_order_pay_cnt,
        SUM(CASE WHEN ur.uid IS NULL THEN CAST(r.amount AS DECIMAL(18,4))
                 ELSE 0 END)                                                  AS old_order_pay_amt
    FROM dwd.dwd_order_paid_d r
    LEFT JOIN dim.dim_region_info_all d ON ...
    LEFT JOIN user_type_info ut         ON ...
    LEFT JOIN user_registration ur      ON r.uid=ur.uid AND r.app_id=ur.app_id AND r.channel=ur.channel
    WHERE /* 同 order_created */ ...
)
-- 全键合并：created ∪ paid（COALESCE 为空 BITMAP / 0）
SELECT k.dt, k.app_id AS app_code, k.channel, k.region, k.device, k.order_type, k.user_type,
       IFNULL(oc.order_create_users, bitmap_empty()), IFNULL(oc.order_create_cnt, 0), IFNULL(oc.order_create_amt, 0),
       IFNULL(op.order_pay_users,    bitmap_empty()), IFNULL(op.order_pay_cnt,    0), IFNULL(op.order_pay_amt, 0),
       IFNULL(op.new_order_pay_users,bitmap_empty()), IFNULL(op.new_order_pay_cnt,0), IFNULL(op.new_order_pay_amt, 0),
       IFNULL(op.old_order_pay_users,bitmap_empty()), IFNULL(op.old_order_pay_cnt,0), IFNULL(op.old_order_pay_amt, 0),
       NOW() AS update_time
FROM (SELECT dt,app_id,channel,region,device,order_type,user_type FROM order_created
      UNION
      SELECT dt,app_id,channel,region,device,order_type,user_type FROM order_paid) k
LEFT JOIN order_created oc ON ...
LEFT JOIN order_paid    op ON ...;
```

完整 ETL 见 `ops_system/04.dws/dws_app_order_d_h/dws_app_order_d_h.sql`（已修正 4 处 `/100` 去除）。

## 4. 海豚调度配置

### 4.1 任务 1：Hourly OVERWRITE（每小时累积当天数据）

| 项 | 值 |
|---|---|
| 节点 | SQL 节点，绑定 `dws_app_order_d_h.sql` |
| Cron | `0 30 0/1 * * ?`（每小时 30 分跑前 1 小时所属日的累积窗口）|
| `partition` | **`p$[yyyyMMdd-1H/yyyyMMdd]`** ← 前 1 小时所属日，**关键**：让 0:30 跑前一天 |
| `slot_start_time` | **`$[yyyy-MM-dd-1H/yyyy-MM-dd 00:00:00]`** ← 前 1 小时所属日的 00:00 |
| `slot_end_time` | `$[yyyy-MM-dd HH:00:00]` ← 当前整点 |

**为什么 partition 用"前 1 小时所属日"而不是"调度时刻所属日"**：

| 场景 | 用 `$[yyyyMMdd]`（错的）| 用 `$[yyyyMMdd-1H/yyyyMMdd]`（对的）|
|---|---|---|
| 11:30 触发 | partition=今天，slot=[今天 00:00, 11:00) ✓ | partition=今天，slot=[今天 00:00, 11:00) ✓ |
| **0:30 触发** | partition=今天，slot=[今天 00:00, 00:00) **空窗** ✗ | **partition=昨天**，slot=[昨天 00:00, 今天 00:00) **完整 24h** ✓ |

如果用调度时刻日期，0:30 跑会切到新一天的空 partition，**昨天 23:00-00:00 这一小时永远没人写**。改用前 1 小时偏移后，0:30 跑等价于"daily T+1 紧急版"，把昨天最后一小时补齐，写到昨天 partition。

### 4.2 任务 2：Daily T+1 OVERWRITE（兜底 + dim 修正）

| 项 | 值 |
|---|---|
| Cron | `0 0 3 * * ?`（每天 03:00 跑昨天）|
| `partition` | `p$[yyyyMMdd-1]` |
| `slot_start_time` | `$[yyyy-MM-dd 00:00:00-1]` |
| `slot_end_time` | `$[yyyy-MM-dd 00:00:00]` |

例：2026-04-30 03:00 触发 → partition=p20260429，slot=[2026-04-29 00:00, 2026-04-30 00:00)

**作用**：
1. OVERWRITE 把 hourly 累积的 segment 整理成单 segment（compaction 减压）
2. 兜迟到事件（dwd 后写入的）
3. 修 hourly 用 dim_user_all 时点的 user_type 漂移

### 4.3 为什么 hourly 0:30 跟 daily 3:00 不能合并

| 时段 | 没有 hourly 0:30 | 有 hourly 0:30（推荐）|
|---|---|---|
| 00:30 ~ 03:00 | 下游看到的是缺最后一小时的快照（昨天 0~23 点）| 下游看到的就是昨天完整 24 小时数据 ✓ |
| 03:00 之后 | daily T+1 跑完，最终态出来 | daily T+1 重新 OVERWRITE 一次，与 hourly 0:30 结果几乎相同（dim 时点差异除外）|

**两者不能合并**：
- hourly 0:30 服务"凌晨业务方需要昨天数据"的场景
- daily 3:00 服务"等 dim 都稳定了再算最终态"的场景
- 时序错开 2.5 小时，各有用途

### 4.4 补历史数据（手工触发）

启动方式：海豚"补数据"模式，选目标日期范围（参数同 daily T+1）。

补 2026-04-25 → 选数据时间 = 2026-04-26（DS 解析 `$[yyyy-MM-dd-1]` = 4-25）。串行执行。

> 注：补数据**只跑 daily 任务**就够（OVERWRITE 完整 24h）；不需要重放 24 个 hourly slot。

## 5. 数据核查规则

### 5.1 daily 跑完核查（hourly 累积态可用同样 SQL）

**核查 A：守恒 + 内部一致性**

```sql
SELECT
    'cnt 守恒'  AS chk,
    SUM(order_pay_cnt)                    AS pay_cnt,
    SUM(new_order_pay_cnt)+SUM(old_order_pay_cnt) AS new_plus_old,
    SUM(order_pay_cnt)-SUM(new_order_pay_cnt)-SUM(old_order_pay_cnt) AS diff
FROM dws.dws_app_order_d_h WHERE dt='${target_dt}'
UNION ALL
SELECT 'amt 守恒（分）',
    ROUND(SUM(order_pay_amt),2),
    ROUND(SUM(new_order_pay_amt)+SUM(old_order_pay_amt),2),
    ROUND(SUM(order_pay_amt)-SUM(new_order_pay_amt)-SUM(old_order_pay_amt),2)
FROM dws.dws_app_order_d_h WHERE dt='${target_dt}'
UNION ALL
SELECT 'distinct uid 守恒',
    BITMAP_UNION_COUNT(order_pay_users),
    BITMAP_UNION_COUNT(BITMAP_OR(BITMAP_UNION_AGG(new_order_pay_users), BITMAP_UNION_AGG(old_order_pay_users))),
    NULL
FROM dws.dws_app_order_d_h WHERE dt='${target_dt}';
```

**期望**：cnt / amt 守恒 diff = 0；distinct uid 可能 ±少量（同 uid 跨 channel 的边界 case，1 个 uid 在 channel A 是 new、channel B 是 old）。

**核查 B：vs dwd 上游对账**

```sql
WITH dh AS (
  SELECT SUM(order_pay_cnt) cnt, ROUND(SUM(order_pay_amt),2) amt,
         BITMAP_UNION_COUNT(order_pay_users) uu
  FROM dws.dws_app_order_d_h WHERE dt='${target_dt}'
), dwd AS (
  SELECT COUNT(DISTINCT event_id) cnt, ROUND(SUM(amount),2) amt,
         COUNT(DISTINCT uid) uu
  FROM dwd.dwd_order_paid_d
  WHERE dt='${target_dt}'
    AND order_type IN ('coin_purchase','vip_subscription')
    AND uid IS NOT NULL AND event_id IS NOT NULL
)
SELECT 'd_h' src, * FROM dh
UNION ALL SELECT 'dwd', * FROM dwd;
```

**期望**：daily T+1 跑完后两行完全一致（cnt / amt / distinct uid 全 0 diff）。hourly 累积态在 23:30 之前应当与 dwd `event_time <= 当前整点` 的子集一致。

### 5.2 头部 app 抽样

```sql
SELECT app_code,
  SUM(order_pay_cnt) pay_cnt,
  ROUND(SUM(order_pay_amt),2) pay_amt_fen,
  BITMAP_UNION_COUNT(order_pay_users) pay_uu,
  ROUND(SUM(new_order_pay_amt),2) new_amt_fen,
  ROUND(SUM(old_order_pay_amt),2) old_amt_fen
FROM dws.dws_app_order_d_h
WHERE dt='${target_dt}'
  AND app_code REGEXP '^[A-Za-z]+-[0-9]+$'
GROUP BY app_code ORDER BY pay_amt_fen DESC LIMIT 10;
```

仅核合法 app_id 格式（`^[A-Za-z]+-[0-9]+$`，参 `feedback_per_app_verification_rule`）。

### 5.3 跟 d 老天表对账（迁移期）

**注意单位换算**：d_h 是分，老 d 表也是分（4-30 已确认），所以**不再有 100 倍差异**——直接 SUM 对比就行。

```sql
WITH dh AS (
  SELECT dt, ROUND(SUM(order_pay_amt),2) amt, SUM(order_pay_cnt) cnt
  FROM dws.dws_app_order_d_h WHERE dt BETWEEN '${start}' AND '${end}'
  GROUP BY dt
), dd AS (
  SELECT dt, ROUND(SUM(order_pay_amt),2) amt, SUM(order_pay_cnt) cnt
  FROM dws.dws_app_order_d   WHERE dt BETWEEN '${start}' AND '${end}'
  GROUP BY dt
)
SELECT COALESCE(dh.dt, dd.dt) dt,
       dh.cnt dh_cnt, dd.cnt d_cnt, dh.cnt - dd.cnt diff_cnt,
       dh.amt dh_amt, dd.amt d_amt, dh.amt - dd.amt diff_amt
FROM dh FULL OUTER JOIN dd USING (dt) ORDER BY dt;
```

**期望**：所有日期 cnt / amt diff 都接近 0（老 d 表跑完终态后差距 < 0.01%）。

## 6. 历史核查记录

### 2026-04-30 上线前核查

**数据现状**：14 天有数据（3-31, 4-18~4-30），4-1~4-17 共 17 天未跑。527,083 行。

**核查结果**：

| # | 项 | 结果 |
|---|---|---|
| 1 | d_h 4-29 vs dwd_order_paid_d 4-29 | cnt / amt（分）/ distinct uid 全 **0 diff** ✅ |
| 2 | d_h vs d 老天表 4-18~4-29 重叠期 cnt | 11/12 天 0 diff，4-25 -1，4-29 +198（d_h 反而更准）✅ |
| 3 | d_h vs d 重叠期 amt | **金额单位差 100 倍（d_h 元 vs d 分）** 🚨 |
| 4 | 修正后（d_h 元 × 100 vs d 分） | 系统性低 0.04~0.11%（hourly 漏 23:00-00:00 这一小时）⚠️ |
| 5 | 内部守恒 cnt / amt | new + old = total ✅ |
| 6 | 内部守恒 distinct uid | new + old = 21,918 vs total 21,917，差 1（跨 channel 同 uid）ℹ️ 业务边界 case |
| 7 | 头部 5 app 抽样 | 数字合理，新老金额拆分跟 app 成熟度匹配 ✅ |

**采取措施**：

| # | 改动 | 状态 |
|---|---|---|
| 1 | ETL SQL 去 4 处 `/100`，单位统一回分 | ✅ 已改（`ops_system/04.dws/dws_app_order_d_h/dws_app_order_d_h.sql`）|
| 2 | 海豚 hourly 调度参数：`partition` / `slot_start_time` 改为"前 1 小时派生" | ⏳ 海豚侧待改 |
| 3 | 海豚补数据 4-1 ~ 4-30 全量重跑（用新 ETL + daily 模式）| ⏳ 待执行 |
| 4 | 跑完后再次 §5.1 核查 B 验证 vs dwd 上游 0 diff | ⏳ 待验证 |
| 5 | metadata.db 列类型修复（cnt 字段标错 BITMAP，实际 BIGINT）| ⏳ 待修 |

## 7. 与 dws_app_user_d_h 的设计差异

两张表都是用户活跃 / 订单聚合的**小时累积模型**，但设计哲学不同：

| 项 | dws_app_user_d_h | dws_app_order_d_h |
|---|---|---|
| 写入语义 | `INSERT INTO`（每小时增量 1 小时窗）+ BITMAP_UNION 自动累加 | `INSERT OVERWRITE`（每小时重写当天 partition，0~当前小时累积窗）|
| hourly slot_start | `$[yyyy-MM-dd HH:00:00-1H]`（前 1 小时整点）| `$[yyyy-MM-dd-1H/yyyy-MM-dd 00:00:00]`（前 1 小时所属日的 00:00）|
| hourly slot_end | `$[yyyy-MM-dd HH:00:00]`（当前整点）| `$[yyyy-MM-dd HH:00:00]`（同左）|
| hourly partition | ETL 内 `DATE(slot_start_time)` 自动定 | 海豚显式传 `p$[yyyyMMdd-1H/yyyyMMdd]` |
| 跨日处理 | 天然正确（slot 跟 partition 都跟着前 1 小时走）| 需要海豚 partition 表达式正确配置（否则 0:30 跑空窗）|
| 优点 | 简洁、增量、跨日天然 | 整 partition OVERWRITE 防 segment 爆 / hourly 跑出来直接是终态 |
| 缺点 | 需要 daily 配合做 compaction | 调度参数稍复杂；hourly 累积扫的事件量大 |

> 不强求两张表统一设计——各自针对的指标性质不同，订单表 `*_cnt`、`*_amt` 都是 BIGINT/DECIMAL SUM，可以直接累积；user 表全是 BITMAP，增量+UNION 更自然。**关键是调度参数都正确处理了跨日**。

## 8. 上线步骤

| # | 操作 | 验证 |
|---|---|---|
| 1 | 部署 ETL SQL（已改 /100，git commit） | git diff |
| 2 | 海豚 hourly 任务参数改为"前 1 小时派生"（§4.1）| 配置审计 |
| 3 | 海豚 daily T+1 任务确认（§4.2）| 配置审计 |
| 4 | **海豚补数据 4-1 ~ 4-30 全量回刷**（daily 模式，串行）| 跑完无报错 |
| 5 | §5.1 核查 B：每天 d_h vs dwd 上游 0 diff | 不达标 → 修 ETL 后回到 #4 |
| 6 | §5.3 d_h vs d 老表对账（4-18~4-29 cnt/amt）| diff 接近 0（旧表 4-29 终态外）|
| 7 | 启动 hourly + daily 调度，观察 24h | hourly run < 30s，daily 正常完成 |
| 8 | metadata 状态 `developing → online` | 元数据库 |
| 9 | 老表迁移（见 §9） | |

## 9. 老表迁移路径

| 老表 | 现状 | 处置 |
|---|---|---|
| `dws.dws_app_order_d` | online，BIGINT 天表 | retired → drop（下游切到 d_h 后）|
| `dwm.dwm_order_paid_d` | retired | 已废弃 |

**切换流程**：
1. d_h 跑稳 1 周，§5.3 d_h vs d 重叠期 cnt / amt diff < 0.01%
2. 下游消费方按本剧本 §3 / §5 切到 d_h（注意单位仍是分，下游 SQL 不用动）
3. 老 d 调度任务暂停（disabled，不删）
4. 观察 1 周下游报表无异常
5. drop 老 d 表，关闭 disabled 调度任务

## 10. 待跟进 / 决策项

1. **命名最终化**：等 `_d_h` 跑稳 + 老 `_d` drop 后，是否把 `dws_app_order_d_h` 改名为 `dws_app_order_d`？建议保持 `_d_h` 不变（区分用户活跃 d_h / 订单 d_h）
2. **`<=` vs `<` 边界**：当前 ETL `event_time <= slot_end_time` 是闭区间，理论上 daily 模式下 `slot_end_time = 第二天 00:00:00` 会包含第二天 0:00:00 那一秒事件。极少出现但语义不严，下次重构时改成 `<`
3. **跨 channel 同 uid 在 new + old 都计 1 次**：当前 ETL 用 `(uid, app_id, channel)` 三键 JOIN `user_registration`，导致同 uid 在 channel A 注册后又在 channel B 付费时，B 的付费会被算 old。这是业务定义决定的；要改成"同 uid 全局只算一次 new"需 ETL 改成 `(uid, app_id)` 二键 JOIN
4. **metadata.db 字段类型采集 bug**：`*_cnt` 在生产是 BIGINT SUM，metadata.db 标 BITMAP。下次跑全量同步时确认列类型识别逻辑
5. **`dws_app_order_d` 老表 4-29 数据缺口**：daily T+1 没跑完终态（比 d_h 少 198 单），需要查下海豚老 d 任务调度

## 11. 维护约定

- ETL SQL 修改 → 必须先 SELECT-only 验证再改 INSERT 部分（参 `feedback_etl_validation_via_select_only`）
- 金额单位**永远是分**——下游需要元自行 / 100；本表 ETL 不再做单位转换
- per-app 核查只对**合法 app_id**（`^[A-Za-z]+-[0-9]+$`）做（参 `feedback_per_app_verification_rule`）
- hourly + daily 双调度 + 补数据 ad-hoc 三个入口必须**互不冲突**（OVERWRITE 同一 partition 不应被多个任务并发写；当前 cron 错开 03:00 daily / 0:30~23:30 hourly 已避免）
- 抽样必须带 event_id（参 `feedback_always_include_event_id_in_samples`）
