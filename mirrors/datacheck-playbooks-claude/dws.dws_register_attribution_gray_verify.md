# 剧本 · 归因灰度对数（channel_apply）

> 表级：灰度 app `dim.dim_app_attribution_config.is_rewrite_channel=1`  
> ETL：`dim_user_attribution_channel_apply_d`（test code 21962007716224）  
> 绑定：`ops_system/06.dim/job_dim_user_attribution_channel_apply/`  
> 默认业务日：**T-1**；用户指定 dt 时替换 `${dt}` / `${app}` / `${non_gray_app}`

## part_01 · 前置：dim 是否够验

```sql
-- 可归因 organic 用户数（须 >0 才能验搬迁）
SELECT COUNT(*) AS organic_rewrite_eligible
FROM dws.dws_register_attribution_result_d r
JOIN dim.dim_user_all u ON r.uid = u.uid AND r.app_id = u.app_id
WHERE r.app_id = '${app}'
  AND r.dt = '${dt}'
  AND r.attribution_status = 'success'
  AND (u.channel = 'organic' OR u.channel IS NULL OR TRIM(u.channel) = '')
  AND LOWER(TRIM(r.attributed_channel)) <> 'organic';
```

**期望**：`organic_rewrite_eligible > 0`。若为 0 且 result 有 success → test dim 缺行，按 lesson 从 prod 同步 success uid 的 `dim_user_all`（验证性补数，非 prod 变更）。

## part_02 · 灰度开关

```sql
SELECT app_id, is_run, is_rewrite_channel
FROM dim.dim_app_attribution_config
WHERE app_id = '${app}';
```

**期望**：`is_run=1` 且 `is_rewrite_channel=1`（开灰 app）。

## part_03 · apply 前 channel 快照

```sql
SELECT IFNULL(channel, '<null>') AS channel, COUNT(*) AS cnt
FROM dim.dim_user_all
WHERE app_id = '${app}'
GROUP BY channel
ORDER BY cnt DESC;
```

记录 `total_before = SUM(cnt)`。

## part_04 · 执行 apply（TASK_ONLY）

- env=test，schedule=`DATE_ADD(${dt}, 1)` 日 `05:20:00`
- task_code=`21962007716224`，`task_dep_type=TASK_ONLY`

## part_05 · 三条验收

### ① 总量守恒

```sql
SELECT COUNT(*) AS total_after FROM dim.dim_user_all WHERE app_id = '${app}';
```

**期望**：`total_after = total_before`。

### ② organic 搬迁

```sql
SELECT COUNT(*) AS rewritten_match
FROM dws.dws_register_attribution_result_d r
JOIN dim.dim_user_all u ON r.uid = u.uid AND r.app_id = u.app_id
WHERE r.app_id = '${app}' AND r.dt = '${dt}'
  AND r.attribution_status = 'success'
  AND LOWER(TRIM(r.attributed_channel)) <> 'organic'
  AND u.channel = r.attributed_channel;
```

**期望**：`rewritten_match` ≈ part_01 的 `organic_rewrite_eligible`（允许少量无归因 success 的 organic 残留）。

### ③ 非灰度 app 不变

对 `${non_gray_app}`（如 SF-01）重复 part_03，apply 前后分布一致。

## part_06 · rewrite_status（可选）

```sql
SELECT rewrite_status, COUNT(*)
FROM dws.dws_register_attribution_result_d
WHERE app_id = '${app}' AND dt = '${dt}' AND attribution_status = 'success'
GROUP BY rewrite_status;
```

**期望**：灰度 apply 后 `1`/`0` 有值；影子期全 NULL。

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-07-01 | 初版；SF-81 test 06-28 516/516 验证通过 |
