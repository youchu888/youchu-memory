# dws.dws_device_tag_d_d · 字段与枚举

> 表类型：设备标签当前态宽表  
> 主键：`(app_id, device_id)`  
> 分区：无（`calc_dt` 为最近重算基准日，非分区键）

---

## 字段清单

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| app_id | VARCHAR(50) | 是 | 应用 ID |
| device_id | VARCHAR(128) | 是 | 设备 ID |
| calc_dt | DATE | 否 | 最近一次重算基准日（T-1） |
| reg_product_id | VARCHAR(50) | 否 | 设备首次注册产品 ID |
| reg_platform | VARCHAR(8) | 否 | 设备首次注册端，见枚举 `reg_platform` |
| reg_channel_code | VARCHAR(128) | 否 | 设备首次注册渠道码 |
| reg_supplier_id | VARCHAR(128) | 否 | 注册供应商 ID（一期同 reg_channel_code） |
| lifecycle_flag | VARCHAR(16) | 否 | 生命周期标签，见枚举 `lifecycle_flag` |
| last_login_date | DATE | 否 | 末次活跃日期 |
| last_3_login_day | INT | 否 | 近 3 天活跃天数 |
| last_7_login_day | INT | 否 | 近 7 天活跃天数 |
| last_15_login_day | INT | 否 | 近 15 天活跃天数 |
| last_30_login_day | INT | 否 | 近 30 天活跃天数 |
| is_play | TINYINT | 否 | 是否有效播放过：0=否，1=是 |
| video_level | VARCHAR(8) | 否 | 观影深度，见枚举 `video_level` |
| last_3_video_day | INT | 否 | 近 3 天有效播放天数 |
| last_7_video_day | INT | 否 | 近 7 天有效播放天数 |
| last_15_video_day | INT | 否 | 近 15 天有效播放天数 |
| last_30_video_day | INT | 否 | 近 30 天有效播放天数 |
| last_3_video_count | INT | 否 | 近 3 天有效播放次数（sid 去重） |
| last_7_video_count | INT | 否 | 近 7 天有效播放次数（sid 去重） |
| last_15_video_count | INT | 否 | 近 15 天有效播放次数（sid 去重） |
| last_30_video_count | INT | 否 | 近 30 天有效播放次数（sid 去重） |
| is_paid | TINYINT | 否 | 是否付费：0=否，1=是（累计充值>0） |
| pay_level | VARCHAR(8) | 否 | 付费分层，见枚举 `pay_level` |
| first_pay_date | DATE | 否 | 首充日期 |
| first_pay_amount | DECIMAL(18,2) | 否 | 首充金额（元） |
| last_pay_date | DATE | 否 | 末次付费日期 |
| total_pay_amount | DECIMAL(18,2) | 否 | 累计付费金额（元） |
| total_pay_count | INT | 否 | 累计付费次数 |
| last_3_pay_amount | DECIMAL(18,2) | 否 | 近 3 天付费金额（元） |
| last_7_pay_amount | DECIMAL(18,2) | 否 | 近 7 天付费金额（元） |
| last_15_pay_amount | DECIMAL(18,2) | 否 | 近 15 天付费金额（元） |
| last_30_pay_amount | DECIMAL(18,2) | 否 | 近 30 天付费金额（元） |
| last_3_pay_count | INT | 否 | 近 3 天付费次数 |
| last_7_pay_count | INT | 否 | 近 7 天付费次数 |
| last_15_pay_count | INT | 否 | 近 15 天付费次数 |
| last_30_pay_count | INT | 否 | 近 30 天付费次数 |
| is_VIP | TINYINT | 否 | 是否订阅过 VIP：0=否，1=是 |
| first_VIP_date | DATE | 否 | 首次订阅日期 |
| first_VIP_amount | DECIMAL(18,2) | 否 | 首次订阅金额（元） |
| last_VIP_date | DATE | 否 | 末次订阅日期 |
| last_VIP_amount | DECIMAL(18,2) | 否 | 末次订阅金额（元） |
| total_VIP_count | INT | 否 | 累计订阅次数 |
| total_VIP_amount | DECIMAL(18,2) | 否 | 累计订阅金额（元） |
| is_ad_click | TINYINT | 否 | 是否广告点击过：0=否，1=是 |
| ad_response | VARCHAR(8) | 否 | 广告反应分层，见枚举 `ad_response` |
| last_3_ad_click | INT | 否 | 近 3 天广告点击次数 |
| last_7_ad_click | INT | 否 | 近 7 天广告点击次数 |
| last_15_ad_click | INT | 否 | 近 15 天广告点击次数 |
| last_30_ad_click | INT | 否 | 近 30 天广告点击次数 |
| update_time | DATETIME | 是 | 行更新时间 |
| tag_set | JSON | 否 | 扩展标签合集（当前未使用，为 NULL） |

---

## 枚举值

### reg_platform

| 值 | 说明 |
|----|------|
| App | 移动端（Android / iOS） |
| Web | Web 端（PC / 浏览器） |

### lifecycle_flag

| 值 | 说明 |
|----|------|
| new | 注册当日 |
| oneday | 注册次日及以后无任何活跃 |
| growth | 注册 2–7 天且有活跃 |
| low | 注册超过 7 天，近 3 天活跃 ≤1 天 |
| stable | 注册超过 7 天，近 3 天活跃 ≥2 天 |
| dormant | 注册超过 7 天，近 7 天无活跃，近 30 天有历史活跃 |
| silent | 注册超过 7 天，近 15 天无活跃，近 30 天有历史活跃 |
| churn | 注册超过 7 天，近 30 天无活跃 |
| reactivated | 过去 7 天无活跃后当日再次活跃 |

### video_level

| 值 | 说明 |
|----|------|
| light | 近 7 天有效播放 1–2 天 |
| mid | 近 7 天有效播放 3–5 天 |
| heavy | 近 7 天有效播放 ≥6 天 |

有效播放定义：单次 `play_duration >= 5` 秒。

### pay_level

| 值 | 说明 |
|----|------|
| low | 累计充值 (0, 500] 元 |
| mid | 累计充值 (500, 5000] 元 |
| high | 累计充值 >5000 元 |

### ad_response

| 值 | 说明 |
|----|------|
| mid | 近 7 天广告点击 1–2 次 |
| high | 近 7 天广告点击 ≥3 次 |

近 7 天点击 0 次时 `ad_response` 为 NULL；是否历史点过看 `is_ad_click`。

### is_play / is_paid / is_VIP / is_ad_click

| 值 | 说明 |
|----|------|
| 0 | 否 |
| 1 | 是 |

---

## 对接说明

| 项 | 说明 |
|----|------|
| 查询主键 | `app_id` + `device_id` |
| 金额单位 | 元（DECIMAL） |
| 日期字段 | `DATE` 格式 `YYYY-MM-DD` |
| 时间字段 | `update_time` 为 `DATETIME` |
| NULL 语义 | 枚举未命中、无行为记录时为 NULL；布尔型用 0/1 |
| tag_set | 预留 JSON 扩展，当前产出为 NULL，对接可忽略 |
