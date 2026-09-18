# dw.dw_user_event_detail_new 元数据规则一致性核查剧本

## 1. 表信息
- 目标表：`dw.dw_user_event_detail_new`
- 业务名：用户事件明细原始表（清洗版本）
- 业务别名：事件明细表新版
- 业务域：原始数据
- 表说明：每行一个事件，含公共字段（事件来源/设备/IP/地理）+ 事件特有 payload（JSON 列）
- 时间字段：`event_time`（事件时间），`create_time`（数据入库时间）
- 分区：按 `dt` 日分区
- 数据环境：
  - 测试环境：`.claude/database/test.cnf`
  - 生产环境：`.claude/database/my.cnf`
- 注：核查时优先用 `event_time` 作为时间界（剧本默认用 `event_time`）；走分区裁剪时可加 `dt` 一起

## 2. 参数约定
- 必填：`dt`（核查日期）—— 同时作为 `event_time >= 'dt 00:00:00' AND event_time < '(dt+1) 00:00:00'` 的边界
- 必填：`env`（`test` / `prod`）—— 决定使用 test.cnf 还是 my.cnf；当前 prod 端表为空，事实上只跑 test
- 选填：`event`（按事件名过滤；不填则核查全部事件）
- 选填：`app_id`（按 app 过滤）

## 3. 元数据规则来源

本地 sqlite：`/Users/arthur/Program/datacenter/dc-parent/metadata/metadata.db`

**核查铁律**：

1. **每次核查前必须重新读取 `glossaryterm` 表**——规则随时可能更新（新增字段 / 改 dataFormat / 加 invalidValues / 改 regexMap），任何缓存或剧本里写死的规则都不能直接信。剧本里给的规则只是"截至维护日期"的快照，不是当前实时态。
2. **必须覆盖全部事件 payload 规则，不能只核公共字段**——公共字段层是规则总集的一部分，事件层（每个事件都有自己的 payload required/format/length 规则）也必须逐一核查。**报告必须列出每个事件的违反统计**，哪怕是 0 违反也要列出来证明已检查；不能因为"高量事件 OK 就推断小量事件也 OK"。
3. **报告输出前要回到本节复核**：是否所有 `term_kind_local='common_field'` 的字段都核了？是否所有 `term_kind_local='event_field'` 的事件都核了？是否还有数据里出现但元数据里没规则的事件（说明事件未登记，要单独提醒）？

### 3.1 公共字段规则

**重要**：必须查 **完整 extension_values JSON**，不要只挑几个 key —— 一个字段可能同时配置多类规则（filterRegex + invalidValues + regexMap + minValue + lengthMin/Max + trimStrategy + defaultValue 等），漏一类就漏一组核查。

```sql
-- 查全（用于核查 SQL 编码前必跑一次）
SELECT name, extension_values FROM glossaryterm
WHERE term_kind_local = 'common_field' AND status_local != 'retired'
ORDER BY name;
```

字段可能出现的所有键（截至 2026-04-28）：
- `isRequired` / `dropOnInvalid` —— 必填 + 行级丢弃
- `filterRegex` —— 命中此 regex 的值 = 非法（注意可能含 PCRE 负向先行 `(?!...)`，要拆解为等价 SQL）
- `invalidValues` —— 黑名单（**不要把 filterRegex 的 `(?!X$)` 中的 X 误加到这里**！例：uid 黑名单只有 `u_1001/stress_user/u_lab`，`'0'` 是 regex 显式排除的合法值）
- `regexMap` —— 清洗映射（如 `(?i)ios → IOS`、`保留 → 其他`、`null → [NULL]`）；ETL 应已经清洗，**核查"清洗后期望值"是否到位**（如 device IN ('IOS','ANDROID','PC','OTHER')）
- `dataFormat` —— TIMESTAMP10/13、DATETIME、NUMBER、PERCENT
- `minValue` —— 数值下限（如 client_ts ≥ 1767196800 = 2026-01-01；event_ts 是毫秒）
- `lengthMax` / `lengthMin` —— 长度上下限
- `trimStrategy` —— 两端 trim（核查时如要严格可加 trim 前后差异检查）
- `defaultValue` —— 清洗失败时的兜底值（如 device→OTHER, channel→organic）

**特别坑**：
- StarRocks REGEXP 不支持 PCRE 负向先行 `(?!...)`，要拆成 `field <> '0' AND field REGEXP '...'`
- `bigint` 类型字段（如 client_ts/event_ts）不能直接 `REGEXP`，用数值范围比较替代
- `uid='0'` 是合法的"未登录态"标记，filterRegex 用 `(?!0$)` 显式排除

### 3.2 事件域字段规则
```sql
-- event_field 规则（按 parent_name = 事件名 分组）
SELECT parent_name AS event_name, name AS field_full_name,
       json_extract(extension_values,'$.isRequired')      AS req,
       json_extract(extension_values,'$.dropOnInvalid')   AS drop_on,
       json_extract(extension_values,'$.filterRegex')     AS filter_re,
       json_extract(extension_values,'$.invalidValues')   AS invalids,
       json_extract(extension_values,'$.dataFormat')      AS fmt,
       json_extract(extension_values,'$.lengthMax')       AS lmax,
       json_extract(extension_values,'$.regexMap')        AS regmap
FROM glossaryterm
WHERE term_kind_local = 'event_field'
ORDER BY parent_name, name;
```
- payload key 命名规则：`payload[name_without_event_prefix]`（即去掉 `event_name.` 前缀）
- 例：`ad_impression.ad_id` → `payload->>ad_id`
- payload 数值字段在数据中以**字符串**形式存储（例：`"play_duration": "0"`）

### 3.3 dataFormat 语义（核查口径）

| 值 | 输入容忍 | 输出要求（清洗后落表的期望） | 核查 SQL |
|---|---|---|---|
| `TIMESTAMP10` | 必须 10 位秒级 | bigint 字段：`field BETWEEN 1000000000 AND 9999999999`<br>varchar/payload：`LENGTH=10 AND REGEXP '^[0-9]+$'` | 长度 ≠ 10 → bad |
| `TIMESTAMP13` | 必须 13 位毫秒 | 同上但是 13 位 | 长度 ≠ 13 → bad |
| `DATETIME` | datetime | 不能 NULL（已类型校验） | `field IS NULL` |
| `NUMBER` | 可解析数字（**含正负小数**） | 纯数字字符串/数值 | `NOT REGEXP '^-?[0-9]+(\\.[0-9]+)?$'` |
| **`PERCENT`** | **带不带 `%` 都合法**（如 `40` 或 `40%` 都是合法上报） | **必须去掉 `%`，输出纯数字** | `field LIKE '%\\%%'` → 清洗失败<br>**不要做 [0,100] 范围检查**（除非该字段单独配 minValue/maxValue） |
| `JSON` | 合法 JSON | JSON | `JSON_VALID(field) = 0` |

**特别说明**：
- `PERCENT` 是"输入容忍 + 输出归一化"复合规则，不要简单按"必须有 %"或"必须 [0,100]"判定 —— 元数据原文："带不带 % 都合格，但输出必须去掉 %"
- payload 数值字段（含 NUMBER/PERCENT）在 JSON 里**以字符串形态**存（如 `"play_progress": "76"`），核查必须 `get_json_string(payload, 'key')` 取出再正则
- bigint 类型字段（如 `client_ts`/`event_ts`）不能用 `REGEXP`，用数值范围比较

## 4. 绑定程序

- **数据来源**：上游事件采集与清洗 ETL（独立于本仓库）
- **下游消费**：dwd 层各事件 detail 表、dws 层 user 行为聚合
- **脏数据应沉淀**：`dwd.dwd_standard_dirty_data_df`（dt = 当日）—— 任何 `dropOnInvalid=ROW` 触发的脏行应转储到此

## 5. 核查 parts

### part_01_common_field_required_and_format
- 目的：公共字段层的 `isRequired` / `filterRegex` / `invalidValues` / `dataFormat` / `lengthMax` 全规则核查
- 判定：任一规则违反占比超过预期阈值（默认零容忍 = 期望 0）→ 失败

#### SQL 模板
```sql
SELECT
  COUNT(*) AS total,
  -- isRequired = TRUE 的字段：NULL/空 检查
  SUM(CASE WHEN event_id IS NULL OR TRIM(event_id)='' THEN 1 ELSE 0 END)              AS req_event_id_null,
  SUM(CASE WHEN event IS NULL OR TRIM(event)='' THEN 1 ELSE 0 END)                    AS req_event_null,
  SUM(CASE WHEN app_id IS NULL OR TRIM(app_id)='' THEN 1 ELSE 0 END)                  AS req_app_id_null,
  SUM(CASE WHEN device_id IS NULL OR TRIM(device_id)='' THEN 1 ELSE 0 END)            AS req_device_id_null,
  SUM(CASE WHEN real_device_id IS NULL OR TRIM(real_device_id)='' THEN 1 ELSE 0 END)  AS req_real_device_id_null,
  SUM(CASE WHEN ip IS NULL OR TRIM(ip)='' THEN 1 ELSE 0 END)                          AS req_ip_null,
  SUM(CASE WHEN client_ts IS NULL OR TRIM(client_ts)='' THEN 1 ELSE 0 END)            AS req_client_ts_null,
  SUM(CASE WHEN country IS NULL OR TRIM(country)='' THEN 1 ELSE 0 END)                AS req_country_null,
  SUM(CASE WHEN event_time IS NULL THEN 1 ELSE 0 END)                                 AS req_event_time_null,
  SUM(CASE WHEN event_ts IS NULL OR TRIM(event_ts)='' THEN 1 ELSE 0 END)              AS req_event_ts_null,
  SUM(CASE WHEN create_time IS NULL THEN 1 ELSE 0 END)                                AS req_create_time_null,
  -- 格式 / 黑名单 / 标准化
  SUM(CASE WHEN app_id IS NOT NULL AND app_id NOT REGEXP '^[A-Z]{2,3}-[0-9]{1,4}$' THEN 1 ELSE 0 END) AS app_id_bad_format,
  SUM(CASE WHEN app_id IN ('-','0','1','155','111','NULL','[appId]','your_app_id') THEN 1 ELSE 0 END) AS app_id_invalid_values,
  SUM(CASE WHEN client_ts IS NOT NULL AND LENGTH(client_ts) <> 13 THEN 1 ELSE 0 END) AS client_ts_bad_len,
  SUM(CASE WHEN device IS NOT NULL AND device <> '' AND device NOT IN ('IOS','ANDROID','PC','OTHER') THEN 1 ELSE 0 END) AS device_not_normalized,
  SUM(CASE WHEN country = '保留' THEN 1 ELSE 0 END) AS country_baoliu,
  SUM(CASE WHEN device_brand IN ('null','unknown') THEN 1 ELSE 0 END) AS dev_brand_raw,
  SUM(CASE WHEN device_model IN ('null','unknown') THEN 1 ELSE 0 END) AS dev_model_raw,
  SUM(CASE WHEN system_name IN ('null','unknown') THEN 1 ELSE 0 END) AS sys_name_raw,
  SUM(CASE WHEN system_version IN ('null','unknown') THEN 1 ELSE 0 END) AS sys_ver_raw,
  SUM(CASE WHEN ip = 'null' THEN 1 ELSE 0 END) AS ip_raw_null,
  SUM(CASE WHEN channel REGEXP '[{}=%/[:space:]]' THEN 1 ELSE 0 END) AS channel_special_chars,
  SUM(CASE WHEN channel IN ('{}','0','-','unknown') THEN 1 ELSE 0 END) AS channel_invalid_values,
  SUM(CASE WHEN channel = 'self' THEN 1 ELSE 0 END) AS channel_self_not_organic,
  -- 长度超限
  SUM(CASE WHEN LENGTH(app_id) > 50 OR (app_id IS NOT NULL AND LENGTH(app_id) < 3) THEN 1 ELSE 0 END) AS app_id_len_bad,
  SUM(CASE WHEN LENGTH(real_device_id) > 256 THEN 1 ELSE 0 END) AS real_dev_too_long,
  SUM(CASE WHEN LENGTH(device_id) > 50 THEN 1 ELSE 0 END) AS device_id_too_long,
  SUM(CASE WHEN LENGTH(event_id) > 32 THEN 1 ELSE 0 END) AS event_id_too_long,
  SUM(CASE WHEN LENGTH(event) > 32 THEN 1 ELSE 0 END) AS event_too_long,
  SUM(CASE WHEN LENGTH(ip) > 100 THEN 1 ELSE 0 END) AS ip_too_long,
  SUM(CASE WHEN LENGTH(country) > 200 THEN 1 ELSE 0 END) AS country_too_long
FROM dw.dw_user_event_detail_new
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY) {{app_filter}};
```

### part_02_event_payload_required_and_format
- 目的：按事件分别核查 payload 字段的 `isRequired` / `dataFormat` / `lengthMax`
- payload key = field 名去掉 `event_name.` 前缀；用 `get_json_string(payload, 'field_name')` 提取（StarRocks 函数）
- 判定：任一事件必填字段缺失率超阈值 → 失败
- **覆盖要求（强制）**：
  - **必须遍历 metadata 中 `term_kind_local='event_field'` 全部事件**（用 `SELECT DISTINCT parent_name FROM glossaryterm WHERE term_kind_local='event_field' AND status_local!='retired'` 拉清单）。每个事件都要出一行违反统计，0 违反也要列出
  - **同时核数据侧的事件 vs 元数据**：`SELECT DISTINCT event FROM dw.dw_user_event_detail_new` 与上面的清单做差集——
    - 数据有但元数据没登记 → 报告里单独章节列出（"未登记事件"）
    - 元数据有但数据没出现 → 当天没数据，备注即可
  - **不允许"只跑高量事件"或抽样**——即使量小也要全跑（payload 规则违反不分量级）

#### SQL 模板（按事件循环；以 ad_impression 为例）
```sql
SELECT 'ad_impression' AS event,
  COUNT(*) AS total,
  SUM(CASE WHEN get_json_string(payload,'ad_id') IS NULL OR get_json_string(payload,'ad_id')='' THEN 1 ELSE 0 END) AS req_ad_id_null,
  SUM(CASE WHEN get_json_string(payload,'ad_slot_key') IS NULL OR get_json_string(payload,'ad_slot_key')='' THEN 1 ELSE 0 END) AS req_ad_slot_key_null,
  SUM(CASE WHEN get_json_string(payload,'ad_type') IS NULL OR get_json_string(payload,'ad_type')='' THEN 1 ELSE 0 END) AS req_ad_type_null,
  SUM(CASE WHEN get_json_string(payload,'creative_id') IS NULL OR get_json_string(payload,'creative_id')='' THEN 1 ELSE 0 END) AS req_creative_id_null,
  SUM(CASE WHEN get_json_string(payload,'page_key') IS NULL OR get_json_string(payload,'page_key')='' THEN 1 ELSE 0 END) AS req_page_key_null,
  SUM(CASE WHEN LENGTH(get_json_string(payload,'ad_id')) > 100 THEN 1 ELSE 0 END) AS ad_id_too_long,
  SUM(CASE WHEN LENGTH(get_json_string(payload,'ad_slot_key')) > 50 THEN 1 ELSE 0 END) AS ad_slot_key_too_long,
  SUM(CASE WHEN LENGTH(get_json_string(payload,'ad_type')) > 50 THEN 1 ELSE 0 END) AS ad_type_too_long,
  SUM(CASE WHEN LENGTH(get_json_string(payload,'creative_id')) > 100 THEN 1 ELSE 0 END) AS creative_id_too_long,
  SUM(CASE WHEN LENGTH(get_json_string(payload,'page_key')) > 512 THEN 1 ELSE 0 END) AS page_key_too_long
FROM dw.dw_user_event_detail_new
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND event = 'ad_impression';
```

#### 各事件覆盖表（必填字段 / 格式 / 长度）
| 事件 | 必填字段 | dataFormat / 范围 | 长度上限 |
|---|---|---|---|
| ad_impression | ad_id, ad_slot_key, ad_type, creative_id, page_key | - | ad_id≤100, ad_slot_key≤50, ad_type≤50, creative_id≤100, page_key≤512 |
| ad_click | ad_id, ad_slot_key, ad_type, creative_id, page_key | - | 同上 |
| advertising | advertising_id, advertising_key, event_type | - | aid/akey≤100, event_type≤32 |
| app_install | trace_id | - | trace_id≤100 |
| app_page_view | page_key, user_type | page_load_time=NUMBER | page_key≤50, user_type≤50 |
| comic_event | comic_behavior_key, comic_id, comic_type_id, read_progress | read_progress=PERCENT, page_no=NUMBER | cbk≤100, cid≤255, ctid≤1024 |
| keyword_click | click_item_id, click_item_type_key, keyword | search_result_count=NUMBER, click_position=NUMBER | cii≤255, citk≤100 |
| keyword_search | keyword, search_id | search_result_count=NUMBER | - |
| landing_page_click | click_coordinates_x/y, click_x/y_percent, landing_page_id, screen_width/height, tab_key | x/y=NUMBER, x/y_percent=PERCENT, screen=NUMBER | landing_page_id≤100 |
| landing_page_view | landing_page_id | - | landing_page_id≤100 |
| navigation | navigation_key | - | navigation_key≤256 |
| novel_event | novel_behavior_key, novel_id | page_no=NUMBER, read_progress=PERCENT | nbk≤100, nid≤255 |
| order_created | amount, create_time, currency, order_id, order_type, product_id | amount=NUMBER, create_time=TIMESTAMP10, coin_quantity=NUMBER | order_id≤100, product_id≤50 |
| page_click | click_page_x/y, click_x/y_percent, page_key, screen_width/height | x/y=NUMBER, x/y_percent=PERCENT, screen=NUMBER | page_key≤50 |
| recommend_list_view | page_key, recommend_content_type | - | page_key≤50 |
| user_login | type | - | - |
| user_register | create_time, type | create_time=TIMESTAMP10 | - |
| video_collect | flag, video_content_type, video_id | - | video_id≤200 |
| video_event | play_duration, play_progress, video_behavior_key, video_content_type, video_duration, video_id | play_duration=NUMBER, play_progress=PERCENT, video_duration=NUMBER | video_id≤200 |
| video_like | flag, video_content_type, video_id | - | video_id≤200 |

> 完整规则随时从 `glossaryterm` 表读取最新。运行核查前用 part_03.1 的 SQL 拉取。

### part_03_dirty_data_sink_reconciliation
- 目的：脏数据沉淀对账 —— 所有 `dropOnInvalid=ROW` 触发的违反应转储到 `dwd.dwd_standard_dirty_data_df`
- 判定：`dwd_standard_dirty_data_df` 行数应**至少**为各违反统计之和；远低于 → ETL 落表逻辑失效

#### SQL
```sql
SELECT 'dirty_sink' AS chk, COUNT(*) AS dirty_rows
FROM dwd.dwd_standard_dirty_data_df WHERE dt = '{{dt}}';
```

### part_04_per_app_distribution
- 目的：按 app 拆分主要违反（per-app verification rule）
- 仅核对**合法 app_id 格式**（`^[A-Z]{2,3}-\d{1,4}$`）；非法 app_id 直接计入 part_01 的 `app_id_bad_format`，不做 per-app 拆分

#### SQL（以公共字段层为例）
```sql
SELECT app_id,
  COUNT(*) AS total,
  SUM(CASE WHEN client_ts IS NOT NULL AND LENGTH(client_ts) <> 13 THEN 1 ELSE 0 END) AS bad_ts,
  SUM(CASE WHEN device IS NOT NULL AND device <> '' AND device NOT IN ('IOS','ANDROID','PC','OTHER') THEN 1 ELSE 0 END) AS bad_device,
  SUM(CASE WHEN channel = 'self' THEN 1 ELSE 0 END) AS chan_self,
  SUM(CASE WHEN real_device_id IS NULL OR TRIM(real_device_id)='' THEN 1 ELSE 0 END) AS rdid_null
FROM dw.dw_user_event_detail_new
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND app_id REGEXP '^[A-Z]{2,3}-[0-9]{1,4}$'
GROUP BY app_id
HAVING bad_ts > 0 OR bad_device > 0 OR chan_self > 0 OR rdid_null > 0
ORDER BY total DESC;
```

### part_05_exception_sampling
- 目的：每类违反抽 ≥ 2 行**带 event_id** 的样本作为佐证
- 规则：所有抽样必须带 `event_id`；payload 类违反需带完整 payload
- 公共字段层每类违反一组样本；payload 层每事件每违反一组

#### SQL 模板（公共字段层）
```sql
-- 例：app_id 不合规
SELECT event_id, event, app_id
FROM dw.dw_user_event_detail_new
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND app_id NOT REGEXP '^[A-Z]{2,3}-[0-9]{1,4}$'
LIMIT 3;
```

#### SQL 模板（payload 层）
```sql
-- 例：keyword_search.search_id NULL
SELECT event_id, app_id, payload
FROM dw.dw_user_event_detail_new
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND event = 'keyword_search'
  AND (get_json_string(payload,'search_id') IS NULL OR get_json_string(payload,'search_id')='')
LIMIT 2;
```

## 6. 报告约定
- 报告目录：`.claude/database/reports/`
- 文件名：`dw_user_event_detail_new__rules_check__{{dt}}.md`
- 报告必含章节：
  1. 总体结论 —— 生效/失效规则一览 + dirty_data_sink 是否对账
  2. 公共字段层违反统计（含必填、格式、黑名单、标准化、长度）
  3. 公共字段层异常样本（每类 ≥ 2 行带 event_id）
  4. 事件域 payload 违反统计（按事件全表 + 严重违规分类表）
  5. payload 异常样本（每事件每违反 ≥ 2 行带 event_id 与完整 payload）
  6. 脏数据沉淀对账
  7. 与上次核查对比（如存在历史报告）
  8. 链接到本剧本

## 7. 剧本维护约定
- 元数据规则变化（glossaryterm 中字段新增/删除/修改）→ 同步更新 part_02 的事件覆盖表
- 新增事件：按事件名扩展 part_02 的 SQL 模板；从 glossaryterm 读最新规则
- StarRocks 语法：JSON 字段提取用 `get_json_string(payload, 'key')`；不要用 `payload->>` 操作符
- per-app 核查：仅 `^[A-Z]{2,3}-\d{1,4}$` 合法 app_id 参与；非法 app_id 计入 `app_id_bad_format`
- payload 数值字段在数据中是字符串：用 `CAST(get_json_string(...) AS DOUBLE)` 校验范围；用 `REGEXP '^-?[0-9]+(\.[0-9]+)?$'` 校验"是数字"
- 每类违反必须带样本佐证（event_id）；payload 类违反必须附完整 payload
- 报告写完不动元数据；如需修复元数据规则，单独走元数据维护流程
