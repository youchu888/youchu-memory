---
name: ddl must sync verify etl
description: Before ALTER TABLE add/drop columns, first identify all ETL writers; DDL and ETL must ship together; gated/shadow features must not reach prod without approval; prefer explicit INSERT column lists.
type: feedback
---
**知秋钦定 · 2026-07-01 · 全员必守**

改表结构（ALTER 加/删列）前，第一动作核对该表被哪些 ETL 写入。尤其 `INSERT OVERWRITE` **不带列清单** 的写法按位置严格匹配表全部列，加一列或删一列 StarRocks analyze 会 0 秒拒写。

判 ETL 是否需同步改；若需改则 **DDL 与 ETL 必须同一次一起上**，禁只上一半。半上线 = prod 必挂（2026-07-01 `rewrite_status` 上 prod 未同步归因结果 ETL → 连锁 ~22 张表阻塞，为活教材）。

影子 / gated 功能的 DDL 不能偷偷上 prod，须等业务拍板（如 `rewrite_status` 本应 test 影子期、知秋定上线时机）。

修法首选：`INSERT` 改 **显式列清单**（前向兼容，以后加列不炸）；临时救急可在 SELECT 补 `NULL AS new_col`，但仍须与 DDL 同批发布。

**Why:** 又初把 `rewrite_status` ALTER 到 prod `dws_register_attribution_result_d`（28 列），归因结果 ETL 仍 27 列无列清单 INSERT → 07-01 05:25 起每次 0 秒失败，连带 `wf_dws_汇总_日` 及两个日报 wf 缺数。

**How to apply:**
1. `rg "INSERT OVERWRITE.*<table>" ops_system/ db/` + 血缘 / `program_mappings.md` 列写表 task。
2. 若 ETL 无显式列清单 → 改 DDL 前必须先改 ETL（或同时发版）。
3. test 验 DDL+ETL+补数 SUCCESS 且有行数后，prod 仍须拍板；影子功能 prod DDL 单独 HOLD。
4. 发布 checklist：`DESC` 列数 = SELECT 列数；显式 `(col1,…)` 与 SELECT 顺序一致。

**关联:** `lessons/2026-07-01-rewrite-status-prod-ddl-etl-mismatch.md`、`lessons/20260609-attribution-flag-column-order.md`
