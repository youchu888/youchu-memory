# Playbook · dws_session_duration_user_d / device_d（v2 合表）

session: `dev-20260729-002`  
默认只查 **T-1**。

## part_01 · 表存在 + 合表关键列

```sql
SELECT table_name, COLUMN_NAME
FROM information_schema.columns
WHERE table_schema='dws'
  AND table_name IN ('dws_session_duration_user_d','dws_session_duration_device_d')
  AND COLUMN_NAME IN (
    'stat_grain','avg_session_duration_sec','avg_daily_duration_sec',
    'duration_bucket','session_cnt','bounce_cnt'
  )
ORDER BY table_name, COLUMN_NAME;
```

**期望**：两表均有 `stat_grain` / 两均值列 / `duration_bucket`。

## part_02 · T-1 两 grain 有数

```sql
SELECT 'user' AS side, stat_grain, COUNT(*) cnt,
       SUM(COALESCE(session_cnt,0)) session_cnt_sum,
       SUM(COALESCE(user_cnt,0)) entity_cnt_sum
FROM dws.dws_session_duration_user_d
WHERE dt = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
GROUP BY stat_grain
UNION ALL
SELECT 'device', stat_grain, COUNT(*),
       SUM(COALESCE(session_cnt,0)),
       SUM(COALESCE(device_cnt,0))
FROM dws.dws_session_duration_device_d
WHERE dt = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
GROUP BY stat_grain;
```

**期望**：每侧 `session` + `daily` 都有行；`cnt > 0`。

## part_03 · daily 无 bucket0

```sql
SELECT 'user' AS side,
       SUM(CASE WHEN stat_grain='daily' AND duration_bucket=0 THEN 1 ELSE 0 END) bad
FROM dws.dws_session_duration_user_d
WHERE dt = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
UNION ALL
SELECT 'device',
       SUM(CASE WHEN stat_grain='daily' AND duration_bucket=0 THEN 1 ELSE 0 END)
FROM dws.dws_session_duration_device_d
WHERE dt = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY);
```

**期望**：`bad = 0`。

## 绑定

- ETL：`dws_session_duration_user_d.sql` / `dws_session_duration_device_d.sql`
- test task：`22357755272832` / `22357755654144`（`wf_dws_汇总_日`）
- 查询看板必须带 `WHERE stat_grain IN ('session','daily')`
