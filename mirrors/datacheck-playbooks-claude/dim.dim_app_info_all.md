# 剧本 · dim.dim_app_info_all

| 项 | 值 |
|----|----|
| 表 | SR `dim.dim_app_info_all` ↔ Paimon `paimon.dim.dim_app_info_all` |
| 业务名 | 应用维表（按天全量快照） |
| 状态 | 已挂 runner；核清收编 2026-11-19 |
| ETL | `spark/06.dim/dim_app_info_all/dim_app_info_all_sync.sql` |
| 调度 | full_chain 步 `dim_app_info_all`，05 槽；海豚维表约 04:50 产出 |
| 主键 | `(dt, app_code)` |
| 参数 | `dt` 默认 **T-1**；未指定禁止扩多日 |

session 副本：`ops_system/spark_migrate/dim_app_info_all/playbook.md`

## part_01_row_count

```sql
-- SR
SELECT COUNT(*) AS cnt FROM dim.dim_app_info_all WHERE dt = '${DT}';
-- Paimon
SELECT COUNT(*) AS cnt FROM paimon.dim.dim_app_info_all WHERE dt = '${DT}';
```

期望：两侧相等且 > 0。

## part_02_primary_key

```sql
SELECT COUNT(*) AS cnt, COUNT(DISTINCT app_code) AS key_cnt
FROM dim.dim_app_info_all WHERE dt = '${DT}';
```

期望：`cnt = key_cnt`。

## part_03_attr_agg

```sql
-- SR：名字用 CHAR_LENGTH
SELECT COUNT(*) AS cnt,
       SUM(IFNULL(app_type,0)) AS s_app_type,
       SUM(IFNULL(paid_type,0)) AS s_paid,
       SUM(IFNULL(status,0)) AS s_status,
       SUM(LENGTH(IFNULL(dept_code,''))) AS s_dept_len,
       SUM(CHAR_LENGTH(IFNULL(app_name,''))) AS s_name_chars
FROM dim.dim_app_info_all WHERE dt = '${DT}';

-- Paimon：名字用 LENGTH（字符）
SELECT COUNT(*) AS cnt,
       SUM(COALESCE(app_type,0)) AS s_app_type,
       SUM(COALESCE(paid_type,0)) AS s_paid,
       SUM(COALESCE(status,0)) AS s_status,
       SUM(LENGTH(COALESCE(dept_code,''))) AS s_dept_len,
       SUM(LENGTH(COALESCE(app_name,''))) AS s_name_chars
FROM paimon.dim.dim_app_info_all WHERE dt = '${DT}';
```

期望：各指标两侧相等。硬规则：禁止 SR `LENGTH(app_name)` 对 Spark `LENGTH`。

## part_04_partition_gap

近期窗口按日 `GROUP BY dt`，看是否断档。  
已知 test 缺 `2026-10-31`（2026-11-19 登记）。

## part_05_source_path

确认 runner 使用 `srViews` / `sr_dim_app`，非 JDBC。

## 报告落地

`.claude/database/reports/dim.dim_app_info_all/validate__<dt>__<ts>.md`

## 变更记录

| 日期 | 说明 |
|------|------|
| 2026-11-19 | 初版：核清收编；T-1=11-18 test/prod 对平 PASS；禁 JDBC；中文 LENGTH 口径 |
