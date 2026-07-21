---
name: db/ 是源代码目录
description: 扫描表的 DDL/ETL 时必须把项目根 db/ 整个目录纳入源代码扫描范围，不只是 ops_system/。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
扫描数据库表的 DDL/ETL 代码归属时，**必须同时覆盖** `ops_system/` 和项目根的 `db/` 两个目录及其所有子目录。

**Why**：之前我做血缘追溯时只扫 `ops_system/`，把 `dim.dim_app_attribution_config` 等表标为"本仓库无"，结果用户告诉我应该扫 `db/`。实际上：
- `dim.dim_app_attribution_config` / `dim.dim_app_attribution_time_config` 的 DDL+种子数据在 `ops_system/04.dws/dws.dws_register_attribution_result_d/ios_mpv_config.sql`（跟着用方目录放，不在 06.dim 下）
- `dim.dim_event` 在 `db/dim/事件code.sql`
- `db/ads/ads.sql` 是合并了 7+ 张 ads 表的 DDL+ETL 单文件，按行号定位
- `db/dws/dws.sql`、`db/dws/用户活跃.sql`、`db/dws/结算详情.sql`、`db/dws/结算数据-flink.sql` 都承载真实生产 ETL
- `db/flink-sql/数据分流.sql` 是从 Kafka 写入 `dw.dw_user_event_detail` 的核心 Flink 作业
- `db/dwd/广告.sql`、`db/dwd/新增活跃用户.sql` 写的渠道专用 dwd

**How to apply**：
1. 表代码归属搜索的 grep 起点必须是 `db ops_system`，不能只 `ops_system`
2. 当某张表"找不到 DDL/ETL"时，**先在 `db/` 全量子目录二次确认**再下结论
3. 写映射文档时，把 `db/` 与 `ops_system/` 都列为源代码根
4. db/ 子目录清单（2026-04-28）：`db/ads`、`db/ods`、`db/dim`、`db/dw`、`db/dwd`、`db/dws`、`db/flink-sql`、`db/paimon`、`db/数据质量`，加根级 `database.sql`、`物化视图.sql`、`flink-paimon.sql`、`test.sql`
