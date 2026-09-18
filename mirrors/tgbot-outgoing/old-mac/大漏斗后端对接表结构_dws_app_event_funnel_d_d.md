# 大漏斗 · 后端对接表结构

> 表名：`dws.dws_app_event_funnel_d_d`  
> 维护：又初 · 2026-08-14  
> 口径字典：http://54.255.236.159:8012/library/metric_big_funnel_event_dictionary

---

## 1. 表概览

| 项 | 说明 |
|----|------|
| 库表 | `dws.dws_app_event_funnel_d_d` |
| 行粒度 | `(dt, app_id, is_new)` 唯一一行 |
| 主键 | `(dt, app_id, is_new)` |
| 分区 | 按 `dt` 日分区 |
| 调度 | 日批 T-1，幂等覆盖当天分区 |
| 规模 | 约 560 app × 3 档 is_new ≈ 1,700 行/天 |

---

## 2. 维度字段（4 列）

| 字段 | 类型 | 说明 |
|------|------|------|
| `dt` | date | 业务日 |
| `app_id` | varchar(50) | 应用 ID |
| `is_new` | tinyint | `1`=新用户（当日注册）· `0`=老用户 · `-1`=无 uid |
| `update_time` | datetime | 本分区写入时刻 |

### is_new 取值

| 值 | 含义 |
|----|------|
| `1` | 新用户：该 uid 注册日 = 当日 |
| `0` | 老用户：注册日早于当日 |
| `-1` | 无 uid，无法判定新老（如部分 app_install / sdk_init） |

---

## 3. 指标字段（18 事件 × 3 = 54 列）

命名：`<事件前缀>_user_cnt` / `_session_cnt` / `_event_cnt`  
类型：`bigint`，无数据填 `0`（非 NULL）。

| 中文 | user_cnt | session_cnt | event_cnt |
|------|----------|-------------|-----------|
| 安装 | `app_install_user_cnt` | `app_install_session_cnt` | `app_install_event_cnt` |
| 注册 | `user_register_user_cnt` | `user_register_session_cnt` | `user_register_event_cnt` |
| 登录 | `user_login_user_cnt` | `user_login_session_cnt` | `user_login_event_cnt` |
| 下单 | `order_created_user_cnt` | `order_created_session_cnt` | `order_created_event_cnt` |
| 支付 | `order_paid_user_cnt` | `order_paid_session_cnt` | `order_paid_event_cnt` |
| 金币消耗 | `coin_consume_user_cnt` | `coin_consume_session_cnt` | `coin_consume_event_cnt` |
| SDK 初始化 | `sdk_init_user_cnt` | `sdk_init_session_cnt` | `sdk_init_event_cnt` |
| 页面浏览 | `app_page_view_user_cnt` | `app_page_view_session_cnt` | `app_page_view_event_cnt` |
| 页面点击 | `page_click_user_cnt` | `page_click_session_cnt` | `page_click_event_cnt` |
| 视频展示 | `video_view_user_cnt` | `video_view_session_cnt` | `video_view_event_cnt` |
| 视频播放 | `video_play_user_cnt` | `video_play_session_cnt` | `video_play_event_cnt` |
| 视频购买 | `video_purchase_user_cnt` | `video_purchase_session_cnt` | `video_purchase_event_cnt` |
| 小说展示 | `novel_view_user_cnt` | `novel_view_session_cnt` | `novel_view_event_cnt` |
| 小说阅读 | `novel_read_user_cnt` | `novel_read_session_cnt` | `novel_read_event_cnt` |
| 小说购买 | `novel_purchase_user_cnt` | `novel_purchase_session_cnt` | `novel_purchase_event_cnt` |
| 漫画展示 | `comic_view_user_cnt` | `comic_view_session_cnt` | `comic_view_event_cnt` |
| 漫画阅读 | `comic_read_user_cnt` | `comic_read_session_cnt` | `comic_read_event_cnt` |
| 漫画购买 | `comic_purchase_user_cnt` | `comic_purchase_session_cnt` | `comic_purchase_event_cnt` |

### 三指标含义

| 后缀 | 计算 |
|------|------|
| `_user_cnt` | `COUNT(DISTINCT uid)`，无 uid 不计入 |
| `_session_cnt` | `COUNT(DISTINCT sid)` |
| `_event_cnt` | `COUNT(*)` 事件条数 |

---

## 4. 查询示例

### 按 app + 业务日查三档

```sql
SELECT *
FROM dws.dws_app_event_funnel_d_d
WHERE dt = '2026-08-03'
  AND app_id = 'SF-81'
ORDER BY is_new;
```

### 合并新老用户（app 级汇总）

```sql
SELECT
  dt,
  app_id,
  SUM(user_register_user_cnt) AS user_register_user_cnt,
  SUM(user_login_user_cnt)    AS user_login_user_cnt,
  SUM(video_play_user_cnt)    AS video_play_user_cnt
FROM dws.dws_app_event_funnel_d_d
WHERE dt = '2026-08-03'
  AND app_id = 'SF-81'
GROUP BY dt, app_id;
```

### 排除无 uid 档（仅 0/1）

```sql
SELECT *
FROM dws.dws_app_event_funnel_d_d
WHERE dt = '2026-08-03'
  AND app_id = 'SF-81'
  AND is_new IN (0, 1);
```

---

## 5. 对接注意

1. **全量用户**：需把 `is_new` 为 `-1/0/1` 三行加总，或按产品要求排除 `-1`。
2. **低覆盖事件**：部分 app 无漫画/小说等功能时，对应指标恒 0 属正常，非缺数。
3. **勿读中间表**：`dws_app_event_funnel_metric_stg_d` 为 ETL 中间层，后端只对接宽表。

---

## 6. DDL（StarRocks 形态）

```sql
CREATE TABLE IF NOT EXISTS dws.dws_app_event_funnel_d_d (
    `dt` date NOT NULL COMMENT "业务日",
    `app_id` varchar(50) NOT NULL COMMENT "应用ID",
    `is_new` tinyint NOT NULL COMMENT "1新/0老/-1无uid",
    `update_time` datetime NOT NULL COMMENT "写入时刻",
    `app_install_user_cnt` bigint NOT NULL DEFAULT "0",
    `app_install_session_cnt` bigint NOT NULL DEFAULT "0",
    `app_install_event_cnt` bigint NOT NULL DEFAULT "0",
    `user_register_user_cnt` bigint NOT NULL DEFAULT "0",
    `user_register_session_cnt` bigint NOT NULL DEFAULT "0",
    `user_register_event_cnt` bigint NOT NULL DEFAULT "0",
    `user_login_user_cnt` bigint NOT NULL DEFAULT "0",
    `user_login_session_cnt` bigint NOT NULL DEFAULT "0",
    `user_login_event_cnt` bigint NOT NULL DEFAULT "0",
    `order_created_user_cnt` bigint NOT NULL DEFAULT "0",
    `order_created_session_cnt` bigint NOT NULL DEFAULT "0",
    `order_created_event_cnt` bigint NOT NULL DEFAULT "0",
    `order_paid_user_cnt` bigint NOT NULL DEFAULT "0",
    `order_paid_session_cnt` bigint NOT NULL DEFAULT "0",
    `order_paid_event_cnt` bigint NOT NULL DEFAULT "0",
    `coin_consume_user_cnt` bigint NOT NULL DEFAULT "0",
    `coin_consume_session_cnt` bigint NOT NULL DEFAULT "0",
    `coin_consume_event_cnt` bigint NOT NULL DEFAULT "0",
    `sdk_init_user_cnt` bigint NOT NULL DEFAULT "0",
    `sdk_init_session_cnt` bigint NOT NULL DEFAULT "0",
    `sdk_init_event_cnt` bigint NOT NULL DEFAULT "0",
    `app_page_view_user_cnt` bigint NOT NULL DEFAULT "0",
    `app_page_view_session_cnt` bigint NOT NULL DEFAULT "0",
    `app_page_view_event_cnt` bigint NOT NULL DEFAULT "0",
    `page_click_user_cnt` bigint NOT NULL DEFAULT "0",
    `page_click_session_cnt` bigint NOT NULL DEFAULT "0",
    `page_click_event_cnt` bigint NOT NULL DEFAULT "0",
    `video_view_user_cnt` bigint NOT NULL DEFAULT "0",
    `video_view_session_cnt` bigint NOT NULL DEFAULT "0",
    `video_view_event_cnt` bigint NOT NULL DEFAULT "0",
    `video_play_user_cnt` bigint NOT NULL DEFAULT "0",
    `video_play_session_cnt` bigint NOT NULL DEFAULT "0",
    `video_play_event_cnt` bigint NOT NULL DEFAULT "0",
    `video_purchase_user_cnt` bigint NOT NULL DEFAULT "0",
    `video_purchase_session_cnt` bigint NOT NULL DEFAULT "0",
    `video_purchase_event_cnt` bigint NOT NULL DEFAULT "0",
    `novel_view_user_cnt` bigint NOT NULL DEFAULT "0",
    `novel_view_session_cnt` bigint NOT NULL DEFAULT "0",
    `novel_view_event_cnt` bigint NOT NULL DEFAULT "0",
    `novel_read_user_cnt` bigint NOT NULL DEFAULT "0",
    `novel_read_session_cnt` bigint NOT NULL DEFAULT "0",
    `novel_read_event_cnt` bigint NOT NULL DEFAULT "0",
    `novel_purchase_user_cnt` bigint NOT NULL DEFAULT "0",
    `novel_purchase_session_cnt` bigint NOT NULL DEFAULT "0",
    `novel_purchase_event_cnt` bigint NOT NULL DEFAULT "0",
    `comic_view_user_cnt` bigint NOT NULL DEFAULT "0",
    `comic_view_session_cnt` bigint NOT NULL DEFAULT "0",
    `comic_view_event_cnt` bigint NOT NULL DEFAULT "0",
    `comic_read_user_cnt` bigint NOT NULL DEFAULT "0",
    `comic_read_session_cnt` bigint NOT NULL DEFAULT "0",
    `comic_read_event_cnt` bigint NOT NULL DEFAULT "0",
    `comic_purchase_user_cnt` bigint NOT NULL DEFAULT "0",
    `comic_purchase_session_cnt` bigint NOT NULL DEFAULT "0",
    `comic_purchase_event_cnt` bigint NOT NULL DEFAULT "0"
)
PRIMARY KEY (`dt`, `app_id`, `is_new`)
PARTITION BY RANGE(`dt`) ()
DISTRIBUTED BY HASH(`app_id`) BUCKETS 8;
```

---

仓库路径：`ops_system/04.dws/dws_app_event_funnel_d_d/dws_app_event_funnel_d_d_ddl.sql`
