# dws.dws_register_attribution_result_d 核查剧本

> **变更记录**
> - 2026-06-30：worker_ant 审核回写方案——`rewrite_status` 落结果表；DAG 禁单独重跑 result；prod 灰度须与 A 类/geo 错开写 `dim_user_all`
> - 2026-06-18：库表变更脚本合并为 `alter_table.sql`（含 DDL/ALTER/配置 migrate）
> - 2026-06-10：口径改为 `attribution_flag=1` 才入围；阈值 40；新增海豚/schedule、DWD 列错位、valid_click 漏斗、两阶段 `is_rewrite_channel` 检查
> - 历史：mvp_v2 打分归因；按 app 独立统计（硬规则 §2.1）

## 1. 表信息
- 表名：`dws.dws_register_attribution_result_d`
- 业务名：渠道归因表
- 状态：上线
- 表说明：自然注册用户与落地页点击/浏览事件的渠道归因结果明细表

## 2. 参数约定
- 必填参数：`dt`
- 选填参数：`app_id`
- 默认过滤逻辑：
  - 仅传 `dt`：核查该日期下当前配置为运行中的全量 app
  - 传 `dt + app_id`：核查指定 app

## 2.1 核查硬规则（必须遵守）

1. **UA 字段只在 `dw.dw_user_event_detail`，不在任何 DWD 表**。所有 UA 有效性 / UA 解析检查必须查 dw 层，禁止再在 `dwd.dwd_landing_page_click_d / view_d / dwd_user_register_d_v2` 里找 `user_agent`。DWD 层这三张表的 `user_agent` 字段按约定恒为 NULL，检查也没意义。
2. **落地页事件（`landing_page_click` / `landing_page_view`）是 H5 事件，只有它们有浏览器 UA**；注册事件（`user_register`）**不看 UA**，注册侧直接核查 `device_brand` / `device_model` / `system_name` / `system_version` 四个字段的有效性（由 SDK 原生 API 提供）。
3. **落地页 UA → 字段解析由 ETL 的 UA parser 完成**（把浏览器 UA 解成 brand/model/system_name/system_version 落进 DWD 四个字段），归因算法再用这四个字段跟注册侧字段做匹配。UA 解析质量核查的正确口径是：**dw 层 UA 非空 → DWD 层四个字段是否解出合理值**。
4. **所有核查必须按 app 独立统计，不做跨 app 总数汇总**。跨 app 总数掩盖了单 app 的埋点/ETL 差异，没有分析价值。报表、抽样、占比全部以 `app_id` 为第一维度。
5. **归因只处理 iOS**（`LOWER(device)='ios'`）。Android 注册 / Android 落地页事件跟归因无关，核查不纳入。
6. **报告文案写事实，不写主观话术**。禁止在报告正文里用"重大发现 / 真正的原因 / 新的原因 / 关键问题 / 核心洞察 / 最严重 / 决定性"等带主观判断色彩的词。**数据本身就是结论**，让表格和数字说话；对话回复里可以用这类表述提示用户，但文件里不留。
7. **注册入围（2026-06-10）**：`dwd.dwd_user_register_d_v2.attribution_flag = 1` 才进入 `reg_base`；`0/NULL` 不参与归因。客户端未上报 flag=1 的 organic iOS 注册不会出现在结果表。
8. **两阶段开关**：`dim.dim_app_attribution_config.is_run=1` 控制计算；`is_rewrite_channel=1` 才由 `dim_user_attribution_channel_apply_d` 回写 `dim.dim_user_all.channel`（影子期全 0）。
9. **结果 0 行先查漏斗**：补数 SUCCESS 但 0 行时，先跑 `part_02b_valid_click_funnel`；`valid_click=0` 属数据特征，非 ETL 故障。
10. **海豚发布后**：REST OFFLINE→PUT→ONLINE 会把 **schedule 打成 OFFLINE**，必须复位；见 `part_00_dolphin_schedule`。
11. **回写状态 `rewrite_status`**（结果表 `TINYINT`）：`1`=成功、`0`=失败、**NULL=不适用**（含已有非 organic 渠道不覆盖、`is_rewrite_channel=0`、未归因）；由 `channel_apply_d` 写入，**禁止加在 `dim_app_attribution_config`**。
12. **DAG 运维锁**：`result_d` → `channel_apply_d` → `metrics_d_d`；result `OVERWRITE` 会清 `rewrite_status`，**禁止单独重跑 result**，必须级联 apply，否则 metrics 少算。
13. **prod 灰度协调**：回写改 `dim_user_all.channel`；与 A 类（`user_type`）/ geo 回填同表并发写入时须错开发版窗口。
14. **影子期验数**：`is_rewrite_channel=0` 时分区 `rewrite_status` 应全 NULL（test 06-28 基准 567 行全 NULL）。

## 3. 绑定程序
- 绑定处理程序：`ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql`
- 渠道回写：`ops_system/06.dim/job_dim_user_attribution_channel_apply/dim_user_attribution_channel_apply_d.sql`
- 绑定配置：`ops_system/04.dws/dws.dws_register_attribution_result_d/alter_table.sql`
- DWD 注册：`ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/`（daily/hourly 须 **INSERT 显式列名**，防 `attribution_flag` 列错位）
- 当前绑定说明：`/datacheck` 执行渠道归因核查时，默认以该 SQL 与配置表为准，不需要额外打开程序。
- 关键逻辑块：
  - `target_apps`：当前参与归因的 app
  - `config_pre`：归因字段分值与通过阈值
  - `time_conf_pre`：时间窗分值
  - `reg_base`：注册基表
  - `scored_clicks`：点击候选与打分
  - `scored_views`：浏览候选与打分
- 源头表约束：涉及 `dw.dw_user_event_detail` 的查询必须带 `event_time` 时间范围，且优先按天查询，禁止全表扫描。
- 程序维护约定：若阈值、分值规则、参与 app、候选匹配逻辑或上游字段映射发生变化，必须同步更新本剧本与 `.claude/database/knowledge.md`。

## 4. 核查 parts

### part_00_dolphin_schedule（日批健康，发布/补数后必跑）
- 目的：确认归因任务实例 SUCCESS，且相关 workflow **schedule 为 ONLINE**（REST 发布会误打 OFFLINE）
- 测试绑定：`wf_dws_汇总_日` code `21869820140416`，task `174729603403591`；DWD 小时 `wf_用户画像_小时` schedule 96
- 判定：当日或 T-1 业务日应有 SUCCESS 实例；schedule `releaseState=ONLINE`；若 OFFLINE 则 `POST /schedules/{id}/online`
- 补数调度：业务日 D → 海豚补数时间填 **D+1 00:00:00**

### part_00b_dwd_attribution_flag_quality（DWD 列与分布）
- 目的：防 `attribution_flag` 列错位（`etl_time` 被 CAST 进 flag）及入围量误判
- 来源表：`dwd.dwd_user_register_d_v2`、`dw.dw_user_event_detail`
- 判定：
  - `attribution_flag` 应为 `0/1/NULL`，**不应**出现 `1248xxxxxx` 量级整数
  - `etl_time` 非 NULL；与源表同 dt 的 0/NULL/1 分布一致
  - 表物理列序若为 `trace_id, etl_time, attribution_flag`（ALTER 追加），ETL 必须显式列名 INSERT

#### SQL：DWD flag 分布 vs 源表
```sql
SELECT attribution_flag, COUNT(*), MAX(etl_time)
FROM dwd.dwd_user_register_d_v2
WHERE dt = '{{dt}}'
GROUP BY attribution_flag;

SELECT CAST(get_json_string(payload,'$.attribution_flag') AS INT) AS src_flag, COUNT(*)
FROM dw.dw_user_event_detail
WHERE event_time >= '{{dt}} 00:00:00' AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND event = 'user_register'
GROUP BY 1;
```

### part_01_config_and_threshold_check
- 目的：核查当前运行 app、默认阈值、字段分值、时间分配置是否按预期加载
- 来源表：`dim.dim_app_attribution_config`、`dim.dim_app_attribution_time_config`
- 核查重点：
  - `is_run = 1` 的 app 清单（15 个大写 app，与 DWD `app_id` 完全一致）
  - `is_rewrite_channel` 影子期应为 0
  - `min_threshold` 是否为 **40**（非历史 70）
  - 品牌/型号/系统/系统版本分值
  - 时间分配置（600/3600/21600/86400 秒）

#### SQL：运行 app 与阈值配置
```sql
WITH target_apps AS (
  SELECT app_id
  FROM dim.dim_app_attribution_config
  WHERE is_run = 1
),
config_pre AS (
  SELECT
    t.app_id,
    COALESCE(bc_s.min_threshold, bc_d.min_threshold) AS min_threshold,
    COALESCE(bc_s.brand_score, bc_d.brand_score) AS brand_score,
    COALESCE(bc_s.model_score, bc_d.model_score) AS model_score,
    COALESCE(bc_s.system_name, bc_d.system_name) AS system_name_score,
    COALESCE(bc_s.system_version, bc_d.system_version) AS system_version_score,
    CASE WHEN bc_s.app_id IS NOT NULL AND bc_s.is_active = 1 THEN 'app_specific' ELSE 'default' END AS config_source
  FROM target_apps t
  LEFT JOIN dim.dim_app_attribution_config bc_s
    ON t.app_id = bc_s.app_id AND bc_s.is_active = 1
  LEFT JOIN dim.dim_app_attribution_config bc_d
    ON bc_d.app_id = 'default'
)
SELECT app_id, is_run, is_rewrite_channel, min_threshold, brand_score, model_score, system_name_score, system_version_score, config_source
FROM config_pre
ORDER BY app_id;
```

#### SQL：时间分配置
```sql
WITH target_apps AS (
  SELECT app_id
  FROM dim.dim_app_attribution_config
  WHERE is_run = 1
),
time_conf_pre AS (
  SELECT
    t.app_id,
    COALESCE(tc_s.max_seconds, tc_d.max_seconds) AS max_seconds,
    COALESCE(tc_s.score, tc_d.score) AS score,
    CASE WHEN tc_s.app_id IS NOT NULL AND tc_s.is_active = 1 THEN 'app_specific' ELSE 'default' END AS config_source
  FROM target_apps t
  CROSS JOIN (
    SELECT max_seconds, score
    FROM dim.dim_app_attribution_time_config
    WHERE app_id = 'default' AND is_active = 1
  ) tc_d
  LEFT JOIN dim.dim_app_attribution_time_config tc_s
    ON t.app_id = tc_s.app_id
   AND tc_s.max_seconds = tc_d.max_seconds
   AND tc_s.is_active = 1
)
SELECT *
FROM time_conf_pre
ORDER BY app_id, max_seconds;
```

### part_02_success_and_failure_summary
- 目的：回答“当前配置 app 是否有归因成功”，并区分 `no_candidate` 与 `score_below_threshold`
- 来源表：`dwd.dwd_user_register_d_v2`、`dws.dws_register_attribution_result_d`
- 关键规则：不能只看结果表，因为结果表只保留 `source_event_id IS NOT NULL` 的注册记录

#### SQL：按 app 汇总成功 / 无候选 / 低分失败
```sql
WITH target_apps AS (
  SELECT app_id
  FROM dim.dim_app_attribution_config
  WHERE is_run = 1
),
reg_base AS (
  SELECT
    r.dt,
    r.app_id,
    r.uid,
    r.event_id AS register_event_id
  FROM dwd.dwd_user_register_d_v2 r
  INNER JOIN target_apps t
    ON r.app_id = t.app_id
  WHERE r.dt = '{{dt}}'
    {{app_filter}}
    AND r.channel = 'organic'
    AND r.uid IS NOT NULL
    AND LOWER(TRIM(r.device)) = 'ios'
    AND r.attribution_flag = 1
),
res AS (
  SELECT
    dt,
    app_id,
    register_event_id,
    attribution_status,
    unattributed_reason
  FROM dws.dws_register_attribution_result_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
)
SELECT
  r.app_id,
  COUNT(*) AS total_reg,
  SUM(CASE WHEN res.register_event_id IS NOT NULL THEN 1 ELSE 0 END) AS candidate_reg,
  SUM(CASE WHEN res.attribution_status = 'success' THEN 1 ELSE 0 END) AS success_reg,
  SUM(CASE WHEN res.unattributed_reason = 'score_below_threshold' THEN 1 ELSE 0 END) AS score_below_threshold_reg,
  SUM(CASE WHEN res.register_event_id IS NULL THEN 1 ELSE 0 END) AS no_candidate_reg
FROM reg_base r
LEFT JOIN res
  ON r.register_event_id = res.register_event_id
GROUP BY r.app_id
ORDER BY total_reg DESC;
```

### part_02b_valid_click_funnel（日更门禁：0 行是否预期）
- 目的：结果表 0 行时，先量化 **ETL 规则内** 的有效 click 候选，避免误判故障
- 规则（与 `click_candidates` 一致）：click.dt ∈ [T-1,T]；click.time < reg.time；间隔 ≤86400s；click.channel 非空且 ≠ organic；reg 须 `attribution_flag=1`
- 判定：`valid_click=0` → 结果 0 行**预期**；`valid_click>0` 但结果 0 行 → 查 ETL/补数顺序

#### SQL：按日 valid_click 漏斗
```sql
SELECT
  r.dt,
  COUNT(DISTINCT r.event_id) AS eligible_regs,
  COUNT(DISTINCT CASE
    WHEN c.event_id IS NOT NULL
     AND c.dt BETWEEN DATE_SUB(r.dt, INTERVAL 1 DAY) AND r.dt
     AND c.event_time < r.event_time
     AND TIMESTAMPDIFF(SECOND, c.event_time, r.event_time) <= 86400
     AND c.channel IS NOT NULL AND TRIM(c.channel) != '' AND LOWER(c.channel) != 'organic'
    THEN r.event_id END) AS valid_click
FROM dwd.dwd_user_register_d_v2 r
INNER JOIN dim.dim_app_attribution_config t ON r.app_id = t.app_id AND t.is_run = 1
LEFT JOIN dwd.dwd_landing_page_click_d c ON r.app_id = c.app_id AND r.ip = c.ip
WHERE r.dt = '{{dt}}'
  {{app_filter}}
  AND r.channel = 'organic'
  AND LOWER(TRIM(r.device)) = 'ios'
  AND r.attribution_flag = 1
GROUP BY r.dt;
```

#### SQL：结果表行数对照
```sql
SELECT dt, COUNT(*) AS result_rows,
  SUM(CASE WHEN attribution_status = 'success' THEN 1 ELSE 0 END) AS success_rows
FROM dws.dws_register_attribution_result_d
WHERE dt = '{{dt}}' {{app_filter}}
GROUP BY dt;
```

### part_03_failure_root_cause_trace
- 目的：对未成功归因做溯源分析，区分 IP 问题、候选缺失、字段缺失、低分失败
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_landing_page_click_d`、`dwd.dwd_landing_page_view_d`、`dws.dws_register_attribution_result_d`
- 已知重点问题：
  - 注册侧内网 IP 导致无法与落地页事件对齐
  - 设备字段缺失/错误导致分数上不去

#### SQL：按 app 拆未成功根因（注册侧视角）
```sql
WITH target_apps AS (
  SELECT app_id
  FROM dim.dim_app_attribution_config
  WHERE is_run = 1
),
reg_base AS (
  SELECT
    r.dt,
    r.app_id,
    r.uid,
    r.event_id AS register_event_id,
    r.event_time AS register_event_time,
    r.ip AS reg_ip,
    r.device_brand,
    r.device_model
  FROM dwd.dwd_user_register_d_v2 r
  INNER JOIN target_apps t
    ON r.app_id = t.app_id
  WHERE r.dt = '{{dt}}'
    {{app_filter}}
    AND r.channel = 'organic'
    AND r.uid IS NOT NULL
    AND LOWER(TRIM(r.device)) = 'ios'
    AND r.attribution_flag = 1
),
candidate_ip AS (
  SELECT DISTINCT app_id, ip
  FROM dwd.dwd_landing_page_click_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 1 DAY) AND '{{dt}}'
    {{app_filter}}
    AND channel IS NOT NULL AND TRIM(channel) != '' AND LOWER(channel) != 'organic'
  UNION
  SELECT DISTINCT app_id, ip
  FROM dwd.dwd_landing_page_view_d
  WHERE dt BETWEEN DATE_SUB('{{dt}}', INTERVAL 1 DAY) AND '{{dt}}'
    {{app_filter}}
    AND channel IS NOT NULL AND TRIM(channel) != '' AND LOWER(channel) != 'organic'
),
res AS (
  SELECT register_event_id, attribution_status, unattributed_reason
  FROM dws.dws_register_attribution_result_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
)
SELECT
  r.app_id,
  COUNT(*) AS total_reg,
  SUM(CASE WHEN r.reg_ip RLIKE '^(10\\.|127\\.|172\\.(1[6-9]|2[0-9]|3[0-1])\\.|192\\.168\\.)' THEN 1 ELSE 0 END) AS private_ip_reg,
  SUM(CASE WHEN r.reg_ip IS NULL OR TRIM(r.reg_ip) = '' THEN 1 ELSE 0 END) AS empty_ip_reg,
  SUM(CASE WHEN c.ip IS NOT NULL THEN 1 ELSE 0 END) AS has_same_ip_candidate_reg,
  SUM(CASE WHEN res.attribution_status = 'success' THEN 1 ELSE 0 END) AS success_reg,
  SUM(CASE WHEN res.unattributed_reason = 'score_below_threshold' THEN 1 ELSE 0 END) AS score_below_threshold_reg,
  SUM(CASE WHEN res.register_event_id IS NULL THEN 1 ELSE 0 END) AS no_candidate_reg
FROM reg_base r
LEFT JOIN candidate_ip c
  ON r.app_id = c.app_id AND r.reg_ip = c.ip
LEFT JOIN res
  ON r.register_event_id = res.register_event_id
GROUP BY r.app_id
ORDER BY total_reg DESC;
```

### part_04a_landing_ua_parse_quality（iOS 落地页 UA 解析质量，按 app）

- **只看 iOS**。归因业务不处理 Android，Android 落地页的 UA 解析质量与归因无关，本 part 不纳入 Android。
- 目的：量化 iOS 落地页 `user_agent` 落到 DWD 四个字段（brand / model / system_name / system_version）的覆盖情况
- 来源表：
  - 源事件 UA：`dw.dw_user_event_detail`（UA 唯一来源；event_time 过滤）
  - 解析结果：`dwd.dwd_landing_page_click_d` / `dwd.dwd_landing_page_view_d`（用 `LOWER(device)='ios'` 过滤）
- iOS 字段天花板：
  - `device_brand = Apple`（UA 里的 "iphone" → 可解）
  - `system_name = iOS`（UA 里的 "iphone os" → 可解）
  - `system_version`（UA 里的 "iphone os X_Y" → 可解）
  - `device_model`：**iOS WebKit UA 不含具体型号**，这是 Apple 从 iOS 13+ 起的隐私策略；落地页 UA 解不出 iPhone 具体型号是正常状态，不算解析失败

#### SQL：按 app 拆解析质量
```sql
WITH src AS (
  SELECT app_id, event_id, event,
    LOWER(user_agent) ua_lower,
    user_agent
  FROM dw.dw_user_event_detail
  WHERE event_time >= '{{dt}} 00:00:00'
    AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
    AND event IN ('landing_page_click', 'landing_page_view')
    {{app_filter}}
),
dwd AS (
  SELECT app_id, event_id, device_model FROM dwd.dwd_landing_page_click_d
  WHERE dt='{{dt}}' {{app_filter}}
  UNION ALL
  SELECT app_id, event_id, device_model FROM dwd.dwd_landing_page_view_d
  WHERE dt='{{dt}}' {{app_filter}}
)
SELECT s.app_id,
  COUNT(*) AS total_events,
  SUM(s.ua_lower IS NOT NULL AND TRIM(s.ua_lower) != '') AS ua_has,
  SUM(s.ua_lower LIKE '%android%') AS ua_android,
  SUM(s.ua_lower LIKE '%iphone%' OR s.ua_lower LIKE '%ipad%') AS ua_ios,
  SUM(d.device_model IS NOT NULL AND TRIM(d.device_model) != ''
      AND LOWER(TRIM(d.device_model)) NOT IN ('unknown','null','none','undefined')) AS model_ok,
  -- Android UA 但 model 没解出：真·ETL 解析失败
  SUM(s.ua_lower LIKE '%android%'
      AND (d.device_model IS NULL OR TRIM(d.device_model) = ''
           OR LOWER(TRIM(d.device_model)) IN ('unknown','null','none','undefined'))) AS android_parse_fail,
  -- iOS UA 没 model：源头限制（不算 ETL 问题）
  SUM((s.ua_lower LIKE '%iphone%' OR s.ua_lower LIKE '%ipad%')
      AND (d.device_model IS NULL OR TRIM(d.device_model) = '')) AS ios_ua_no_model
FROM src s
LEFT JOIN dwd d ON s.app_id=d.app_id AND s.event_id=d.event_id
GROUP BY s.app_id
ORDER BY android_parse_fail DESC;
```

### part_04b_landing_channel_illegality（落地页 channel 非法值，按 app）

- 目的：量化 落地页 `dwd.dwd_landing_page_click_d / view_d` channel 字段的非法值分布，按 app
- 非法值判定：
  - `{}` / `null` / NULL / 空串 → 完全丢，不可恢复
  - `{"pc":"xxx"}` / `{" dc":"xxx"}` → JSON-like，内含真实渠道码，ETL 可解析恢复
  - `{"hasEnterRiskWarnings":"..."}` 等其他 JSON → 风控/状态标志错写到 channel，不可恢复

#### SQL：按 app × 表 × 非法类型
```sql
SELECT app_id, src,
  COUNT(*) total_n,
  SUM(channel IS NULL OR TRIM(channel)='') empty_n,
  SUM(channel = '{}') empty_json_n,
  SUM(channel LIKE '{"pc":%' OR channel LIKE '{" dc":%' OR channel LIKE '{"dc":%') recoverable_json_n,
  SUM(channel LIKE '{%' AND channel NOT LIKE '{"pc":%' AND channel NOT LIKE '{" dc":%' AND channel NOT LIKE '{"dc":%' AND channel != '{}') other_json_n,
  ROUND(SUM(channel IS NULL OR TRIM(channel)='' OR channel LIKE '{%')*100.0/COUNT(*),2) illegal_pct
FROM (
  SELECT app_id, 'click' src, channel FROM dwd.dwd_landing_page_click_d
    WHERE dt='{{dt}}' {{app_filter}}
  UNION ALL
  SELECT app_id, 'view', channel FROM dwd.dwd_landing_page_view_d
    WHERE dt='{{dt}}' {{app_filter}}
) u
GROUP BY app_id, src
ORDER BY app_id, src;
```

### part_04c_success_channel_illegality（归因成功里 channel 不合规，按 app）

- 目的：看已被判定为 success 的归因结果，有多少条 `attributed_channel` 本身是脏值（JSON-like / 空）
- 这些成功行技术上归因正确（IP 匹配 + 设备字段过分），但下游按渠道汇总仍然污染

#### SQL：按 app 拆
```sql
SELECT app_id,
  COUNT(*) success_n,
  SUM(attributed_channel IS NULL OR TRIM(attributed_channel)='') empty_n,
  SUM(attributed_channel = '{}') empty_json_n,
  SUM(attributed_channel LIKE '{"pc":%' OR attributed_channel LIKE '{" dc":%' OR attributed_channel LIKE '{"dc":%') recoverable_json_n,
  SUM(attributed_channel LIKE '{%' AND attributed_channel != '{}'
      AND attributed_channel NOT LIKE '{"pc":%'
      AND attributed_channel NOT LIKE '{" dc":%'
      AND attributed_channel NOT LIKE '{"dc":%') other_json_n,
  SUM(attributed_channel LIKE '{%' OR attributed_channel IS NULL OR TRIM(attributed_channel)='') illegal_total_n,
  ROUND(SUM(attributed_channel LIKE '{%' OR attributed_channel IS NULL OR TRIM(attributed_channel)='')*100.0/COUNT(*),2) illegal_pct
FROM dws.dws_register_attribution_result_d
WHERE dt='{{dt}}' AND attribution_status='success' {{app_filter}}
GROUP BY app_id ORDER BY success_n DESC;
```

### part_04_source_field_quality_check
- 目的：检查归因依赖字段在注册侧、点击侧、浏览侧、源头事件侧的有效性
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_landing_page_click_d`、`dwd.dwd_landing_page_view_d`、`dw.dw_user_event_detail`
- 当前约束：涉及 `dw.dw_user_event_detail` 的 SQL 必须带 `event_time` 范围，建议按天查
- 当前风险提示：
  - DWD 层 `user_agent` 可能未保留，不能把 UA 有效率直接当成 DWD 质量证明
  - `system_name/system_version` 是否在线上 DWD 真实存在，需先通过实际查询确认

#### SQL：注册侧与点击侧字段有效率
```sql
WITH reg_field_stats AS (
  SELECT
    app_id,
    COUNT(1) AS total_reg,
    SUM(CASE WHEN ip IS NOT NULL AND TRIM(ip) != '' THEN 1 ELSE 0 END) AS v_ip_r,
    SUM(CASE WHEN device_brand IS NOT NULL AND LOWER(TRIM(device_brand)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_brand_r,
    SUM(CASE WHEN device_model IS NOT NULL AND LOWER(TRIM(device_model)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_model_r
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    {{app_filter}}
    AND channel = 'organic'
    AND LOWER(TRIM(device)) = 'ios'
    AND attribution_flag = 1
  GROUP BY app_id
),
click_field_stats AS (
  SELECT
    app_id,
    COUNT(1) AS total_click,
    SUM(CASE WHEN ip IS NOT NULL AND TRIM(ip) != '' THEN 1 ELSE 0 END) AS v_ip_c,
    SUM(CASE WHEN device_brand IS NOT NULL AND LOWER(TRIM(device_brand)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_brand_c,
    SUM(CASE WHEN device_model IS NOT NULL AND LOWER(TRIM(device_model)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_model_c
  FROM dwd.dwd_landing_page_click_d
  WHERE dt = '{{dt}}'
    {{app_filter}}
    AND channel IS NOT NULL AND TRIM(channel) != '' AND LOWER(channel) != 'organic'
    AND LOWER(TRIM(device)) = 'ios'
  GROUP BY app_id
)
SELECT
  r.app_id,
  r.total_reg AS total_reg,
  ROUND(r.v_ip_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_ip_valid_pct,
  ROUND(r.v_brand_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_brand_valid_pct,
  ROUND(r.v_model_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_model_valid_pct,
  c.total_click AS total_click,
  ROUND(c.v_ip_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_ip_valid_pct,
  ROUND(c.v_brand_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_brand_valid_pct,
  ROUND(c.v_model_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_model_valid_pct
FROM reg_field_stats r
INNER JOIN click_field_stats c
  ON r.app_id = c.app_id
ORDER BY total_reg DESC;
```

#### SQL：源头事件侧 UA / 系统字段检查（必须带 event_time）
```sql
SELECT
  app_id,
  event,
  COUNT(*) AS total_events,
  SUM(CASE WHEN user_agent IS NOT NULL AND TRIM(user_agent) != '' THEN 1 ELSE 0 END) AS ua_non_empty_rows,
  SUM(CASE WHEN system_name IS NOT NULL AND TRIM(system_name) != '' THEN 1 ELSE 0 END) AS system_name_non_empty_rows,
  SUM(CASE WHEN system_version IS NOT NULL AND TRIM(system_version) != '' THEN 1 ELSE 0 END) AS system_version_non_empty_rows,
  SUM(CASE WHEN ip IS NOT NULL AND TRIM(ip) != '' THEN 1 ELSE 0 END) AS ip_non_empty_rows
FROM dw.dw_user_event_detail
WHERE event_time >= '{{dt}} 00:00:00'
  AND event_time < DATE_ADD('{{dt}}', INTERVAL 1 DAY)
  AND event IN ('user_register', 'landing_page_click', 'landing_page_view')
GROUP BY app_id, event
ORDER BY total_events DESC;
```

### part_05_candidate_app_discovery
- 目的：发现“最有可能归因成功”的 app，作为后续加入配置观察的候选集
- 来源表：`dwd.dwd_user_register_d_v2`、`dwd.dwd_landing_page_click_d`
- 设计原则：
  - 以 `ip/device_brand/device_model` 为主
  - `system_name/system_version` 仅在确认线上表真实存在且有效时再启用
  - 不把 `user_agent` 当核心候选指标

#### SQL：候选 app 发现（基础版）
```sql
WITH reg_field_stats AS (
  SELECT
    app_id,
    COUNT(1) AS total_reg,
    SUM(CASE WHEN ip IS NOT NULL AND TRIM(ip) != '' THEN 1 ELSE 0 END) AS v_ip_r,
    SUM(CASE WHEN device_brand IS NOT NULL AND LOWER(TRIM(device_brand)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_brand_r,
    SUM(CASE WHEN device_model IS NOT NULL AND LOWER(TRIM(device_model)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_model_r
  FROM dwd.dwd_user_register_d_v2
  WHERE dt = '{{dt}}'
    AND channel = 'organic'
    AND LOWER(TRIM(device)) = 'ios'
    AND attribution_flag = 1
  GROUP BY app_id
),
click_field_stats AS (
  SELECT
    app_id,
    COUNT(1) AS total_click,
    SUM(CASE WHEN ip IS NOT NULL AND TRIM(ip) != '' THEN 1 ELSE 0 END) AS v_ip_c,
    SUM(CASE WHEN device_brand IS NOT NULL AND LOWER(TRIM(device_brand)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_brand_c,
    SUM(CASE WHEN device_model IS NOT NULL AND LOWER(TRIM(device_model)) NOT IN ('', 'unknown', 'Unknown', 'null', 'none', 'undefined') THEN 1 ELSE 0 END) AS v_model_c
  FROM dwd.dwd_landing_page_click_d
  WHERE dt = '{{dt}}'
    AND channel IS NOT NULL AND TRIM(channel) != '' AND LOWER(channel) != 'organic'
    AND LOWER(TRIM(device)) = 'ios'
  GROUP BY app_id
)
SELECT
  r.app_id,
  r.total_reg AS reg_total,
  ROUND(r.v_ip_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_ip_valid_pct,
  ROUND(r.v_brand_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_brand_valid_pct,
  ROUND(r.v_model_r * 100.0 / NULLIF(r.total_reg, 0), 2) AS reg_model_valid_pct,
  c.total_click AS click_total,
  ROUND(c.v_ip_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_ip_valid_pct,
  ROUND(c.v_brand_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_brand_valid_pct,
  ROUND(c.v_model_c * 100.0 / NULLIF(c.total_click, 0), 2) AS click_model_valid_pct
FROM reg_field_stats r
INNER JOIN click_field_stats c
  ON r.app_id = c.app_id
WHERE (
    (r.v_ip_r > 0 AND c.v_ip_c > 0)
    OR (r.v_brand_r > 0 AND c.v_brand_c > 0)
    OR (r.v_model_r > 0 AND c.v_model_c > 0)
)
ORDER BY reg_total DESC;
```

## 5. 报告约定
- 结果报告目录：`.claude/database/reports/dws.dws_register_attribution_result_d/`
- 建议文件名：
  - 无 app_id：`validate__{{dt}}__{{timestamp}}.md`
  - 有 app_id：`validate__{{dt}}__app_{{app_id}}__{{timestamp}}.md`
- 报告需包含：
  1. 结论：明确当前配置 app 是否存在归因成功，以及核心失败原因
  2. 核查大类汇总：至少包含“配置核查”“成功率核查”“失败根因核查”“字段质量核查”“候选 app 发现”
  3. 逐条规则结果：每条规则要给出核验范围、异常量/成功量、结论
  4. 抽样证明：成功样本、低分样本、无候选样本、字段缺失样本
  5. 问题与处理建议：区分配置问题、数据质量问题、埋点问题、ETL 问题
- 报告中的所有结论都应带数据，不能只写口头判断。

## 6. 剧本维护约定
- Canonical 路径：本文件；dev session 副本：`ops_system/04.dws/dws.dws_register_attribution_result_d/playbook.md`
- 当主处理程序、配置表结构、阈值、分值、**attribution_flag 入围口径**、候选匹配逻辑、结果表保留策略变更时，必须同步更新本剧本。
- 涉及 `dw.dw_user_event_detail` 的核查 SQL 必须带 `event_time` 时间范围，且优先按天查询。
- 若归因脚本现状与已确认业务口径不一致，必须显式记录“待核对点”，不能静默覆盖。
- **每次 `/datacheck` 核查认可后**：新增 part 或修订期望，在文首「变更记录」留一行（见 `.cursor/rules/datacheck-playbook.mdc`）。

## 7. 基准实测（供对比）

| 环境 | 日期 | 说明 |
|------|------|------|
| 测试 | 2026-06-02~06-09 | 无 `attribution_flag=1` 注册 → 结果 0 行，valid_click=0，符合预期 |
| 生产 | 2026-06-09 | 白名单 organic iOS flag=1 = 594（全部 JHG-001）；旧口径 success≈2934/日 |
| 生产 | 2026-06-05~06-09 | 旧口径日行数 3807~4767，success 约 81% |
