# 设备标签 v2 设计文档

> 版本：v2 · 日期：2026-07-21 · 作者：又初

---

## 一、数据流总览

```
【源层】
dwd_app_page_view_d / dwd_user_watch_video / dwd_order_paid_d
dwd_ad_click_h / dwd_user_register_d / dwd_user_login_d
         ↓
【Job① DWM 日增量 · 6 张 · 每日扫当天分区】
dwm_device_active_d_d   dwm_device_video_d_d   dwm_device_order_d_d
dwm_device_ad_d_d       dwm_device_register_d   dwm_device_pay_sum_d
         ↓
【Job①b uid 桥接 · 2 张】
dwm_device_uid_map_d（PK） + dwm_device_uid_map_delta_d_d（日分区）
         ↓
【Job② 键池物化 · 1 张】
device_tag_merge_keys_di（当日要刷新的 device 清单）
         ↓
【Job③ 宽表 merge · 读 merge_keys × DWM × prev】
dws_device_tag_d_d（主宽表 PK，过 enroll_gate 才写入）
dwm_device_staging_d_d（未过闸门，7d TTL）
```

**关键约定**
- 所有 DWM 按 `device_id` 聚合，充值/播放/广告均为**设备维合计**（不拆 uid）
- `dim_user_all` 不在主数据流里；uid 关联只走 `uid_map`，且为可选桥接
- `merge_keys` 对应用户标签的 `update_pool`，因设备量大物化成表

---

## 二、表数据字典

### 1. dwm_device_register_d（设备首见 · PK 表）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| first_seen_dt | date | dwd 首条事件 dt | 设备在系统首次出现日 |
| register_dt | date | dwd_user_register_d | 有注册事件才填，否则 NULL |
| platform | varchar(16) | dwd 事件字段 | android / ios / web |
| channel_code | varchar(64) | dwd 事件字段（register/page_view 带渠道） | 首见来源渠道，不从 dim_user 取 |
| raw_uid | varchar(32) | dwd 注册事件 uid 字段 | 可空；只用于写 uid_map，宽表不依赖 |
| updated_dt | date | ETL 写入日 | 最后更新日 |

**PK**：(app_id, device_id) 无分区，HASH(app_id, device_id) 64 桶

---

### 2. dwm_device_active_d_d（当日活跃）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| active_cnt | int | COUNT(page_view 事件) | 当日 PV 次数 |
| session_cnt | int | COUNT(DISTINCT sid) | 当日会话数 |
| platform | varchar(16) | dwd | 当日登录端别 |

**来源**：`dwd_app_page_view_d` 按 `device_id` GROUP BY，无需 uid

---

### 3. dwm_device_video_d_d（当日播放）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| play_cnt | int | COUNT(video_event) | 当日总播放次数（多 uid 合计） |
| valid_play_cnt | int | 四条件过滤后 COUNT | 有效播放次数 |
| is_valid_play_day | tinyint | valid_play_cnt > 0 ? 1 : 0 | 是否有效播放日 |
| total_play_duration | bigint | SUM(play_duration_ms) | 当日总播放时长（毫秒） |

**来源**：`dwd_user_watch_video` 按 `device_id` GROUP BY；多 uid 观看全合计

---

### 4. dwm_device_order_d_d（当日充值）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| order_cnt | int | COUNT(order_paid 事件) | 当日充值笔数（多 uid 合计） |
| order_amt | bigint | SUM(amount) 单位分 | 当日充值金额合计 |
| first_order_time | datetime | MIN(pay_time) | 当日首笔时间 |
| last_order_time | datetime | MAX(pay_time) | 当日末笔时间 |
| is_paid_day | tinyint | order_cnt > 0 ? 1 : 0 | 是否付费日 |

**来源**：`dwd_order_paid_d` 按 `device_id` GROUP BY；一台设备所有 uid 充值全合计

---

### 5. dwm_device_ad_d_d（当日广告）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| ad_click_cnt | int | COUNT(ad_click 事件) | 当日广告点击次数 |
| ad_impression_cnt | int | COUNT(ad_impression 事件) | 当日广告曝光次数 |

**来源**：`dwd_ad_click_h` 按 `device_id` GROUP BY

---

### 6. dwm_device_pay_sum_d（累计付费 · PK 表）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| total_pay_amt | bigint | SUM 累计 | 设备历史总充值金额（分） |
| total_pay_cnt | int | COUNT 累计 | 历史总充值笔数 |
| first_pay_dt | date | MIN(pay_time) | 首次付费日 |
| last_pay_dt | date | MAX(pay_time) | 最近付费日 |
| is_paid | tinyint | total_pay_cnt > 0 ? 1 : 0 | 是否付费设备 |
| updated_dt | date | ETL 写入日 | 最后更新日 |

**PK**：(app_id, device_id) 无分区，UPSERT 累计更新；只服务已入册设备

---

### 7. dwm_device_uid_map_d（uid 桥接 · PK 表）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| latest_uid | varchar(32) | 最近 register/login 事件 uid | 当前绑定 uid，可空 |
| uid_cnt | int | COUNT(DISTINCT uid) 历史累计 | 历史绑过几个不同 uid |
| last_uid_dt | date | MAX(event_dt) | 最后一次 uid 变更日 |

**用途**：下游需关联用户侧时，通过此表取 uid → 查 dim_user_all；宽表主链不依赖

---

### 8. dwm_device_uid_map_delta_d_d（uid 变更增量）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| uid | varchar(32) | dwd 事件 | 当日产生 uid 关联的值 |
| event_type | varchar(16) | 事件名 | register / login |

**用途**：只记今天有 uid 动作的 device，供 merge_keys 增量取键，避免全量扫 uid_map

---

### 9. device_tag_merge_keys_di（当日刷新键池）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| calc_dt | date | 分区键 | 计算日 |
| app_id | varchar(32) | — | 要刷新的 app |
| device_id | varchar(64) | — | 要刷新的设备 |
| key_type | varchar(16) | 规则判定 | delta / expiry_7d / expiry_15d / expiry_30d / boundary |

**key_type 说明**

| 值 | 含义 |
|----|------|
| delta | 当日有活跃/播放/充值/广告信号，需更新指标 |
| expiry_7d | 7d 窗口即将滑出，需重算 active_days_7d |
| expiry_15d | 15d 窗口滑出 |
| expiry_30d | 30d 窗口滑出 |
| boundary | lifecycle 状态翻转（0→1 或 1→0），需刷新宽表 |

**对应用户标签的 update_pool**；设备量大，物化成日分区表而非 CTE

---

### 10. dwm_device_staging_d_d（未入册候选）

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| dt | date | 分区键 | 业务日 |
| app_id | varchar(32) | dwd | PK |
| device_id | varchar(64) | dwd | PK |
| raw_first_seen_dt | date | dwd 首条事件 | 首次见到该设备的日期 |
| active_cnt_7d | int | 近 7 日 PV 次数 | 积累活跃信号 |
| gate_miss_reason | varchar(32) | 规则判定 | 未过 enroll_gate 的原因 |

**TTL**：7 天，超期自动清理；过了 enroll_gate 才升入宽表

---

### 11. dws_device_tag_d_d（设备标签宽表 · 最终产出）

| 分类 | 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|------|
| **主键** | app_id | varchar(32) | — | PK |
| | device_id | varchar(64) | — | PK |
| **入册** | enroll_dt | date | 首次过 enroll_gate 当日 | 运营认可的新增日（非 first_seen） |
| | is_new_enrolled | tinyint | enroll_dt = 当日 | 当日是否新增设备 |
| **生命周期** | first_seen_dt | date | dwm_device_register_d | 系统首见日 |
| | lifecycle_flag | varchar(16) | 规则计算 | new / active / returning / dormant / lost |
| | last_active_dt | date | dwm_device_active_d_d MAX | 最近活跃日 |
| **活跃窗口** | active_days_7d | int | 近 7d active 表聚合 | 7 日内活跃天数 |
| | active_days_15d | int | 近 15d active 表聚合 | 15 日内活跃天数 |
| | active_days_30d | int | 近 30d active 表聚合 | 30 日内活跃天数 |
| | rolling_active_days | int | 累计 | 累计活跃天数 |
| **播放** | valid_play_days_7d | int | 近 7d video 表聚合 | 7 日内有效播放天数 |
| | total_valid_play_cnt | int | 累计 | 累计有效播放次数 |
| | avg_play_duration_7d | bigint | 近 7d video 表 SUM/天数 | 7 日均播放时长（毫秒） |
| **付费** | is_paid | tinyint | dwm_device_pay_sum_d | 是否付费设备 |
| | first_pay_dt | date | dwm_device_pay_sum_d | 首次付费日 |
| | last_pay_dt | date | dwm_device_pay_sum_d | 最近付费日 |
| | total_pay_amt | bigint | dwm_device_pay_sum_d | 设备维历史总充值（分） |
| | total_pay_cnt | int | dwm_device_pay_sum_d | 历史总充值笔数 |
| **广告** | ad_click_cnt_7d | int | 近 7d ad 表聚合 | 7 日广告点击次数 |
| **来源** | platform | varchar(16) | dwm_device_register_d | 主要端别 |
| | channel_code | varchar(64) | dwm_device_register_d | 首见渠道 |
| **桥接（慎用）** | latest_uid | varchar(32) | uid_map_d（可选列） | 最近绑定 uid，不做 JOIN 条件 |
| **系统** | updated_dt | date | ETL 写入日 | 最后更新日 |

**PK**：(app_id, device_id) 无分区，HASH(app_id, device_id) 128~256 桶

**enroll_gate 规则（三选一即入册）**
- G1：当日有注册事件且 uid 非空
- G2：近 7 日内活跃天数 ≥ 2（排除一次性落地页噪声）
- G3：当日有付费/有效播放/广告点击信号

---

## 三、表关系一览

| 表 | PK | 分区 | 桶 | 更新方式 |
|----|----|----|----|----|
| dwm_device_register_d | (app_id, device_id) | 无 | HASH 64 | UPSERT |
| dwm_device_active_d_d | (dt, app_id, device_id) | 按 dt 日 | HASH 64 | INSERT OVERWRITE |
| dwm_device_video_d_d | (dt, app_id, device_id) | 按 dt 日 | HASH 64 | INSERT OVERWRITE |
| dwm_device_order_d_d | (dt, app_id, device_id) | 按 dt 日 | HASH 64 | INSERT OVERWRITE |
| dwm_device_ad_d_d | (dt, app_id, device_id) | 按 dt 日 | HASH 64 | INSERT OVERWRITE |
| dwm_device_pay_sum_d | (app_id, device_id) | 无 | HASH 64 | UPSERT |
| dwm_device_uid_map_d | (app_id, device_id) | 无 | HASH 64 | UPSERT |
| dwm_device_uid_map_delta_d_d | (dt, app_id, device_id) | 按 dt 日 | HASH 64 | INSERT OVERWRITE |
| device_tag_merge_keys_di | (calc_dt, app_id, device_id) | 按 calc_dt 日 | HASH 64 | INSERT OVERWRITE |
| dwm_device_staging_d_d | (dt, app_id, device_id) | 按 dt 日（7d TTL） | HASH 64 | INSERT OVERWRITE |
| dws_device_tag_d_d | (app_id, device_id) | 无 | HASH 128~256 | UPSERT |

---

## 四、与用户标签的对比

| 维度 | 用户标签 | 设备标签 v2 |
|------|----------|------------|
| 粒度 | uid | device_id |
| 新增判定 | register 事件 register_dt | enroll_date（过 enroll_gate） |
| 多账号处理 | 一 uid 一行 | 一 device 合计所有 uid |
| update_pool | SQL CTE（不落表） | merge_keys 物化表（量大） |
| dim 依赖 | 用 dim_user_all 补渠道 | 直接从 dwd 事件取，不走 dim_user |
| uid 关联 | 天然有 uid | 经 uid_map 桥接，下游慎用 |
