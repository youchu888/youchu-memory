---
name: Project uses StarRocks exclusively
description: dc-parent project is pure StarRocks; never write MySQL/PostgreSQL/Hive SQL dialect that StarRocks doesn't support
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
所有 SQL 必须符合 StarRocks 语法，不要混用 MySQL/PostgreSQL/Hive 等其他方言的独有用法。

**Why:** 用户明确指出 dc-parent 整个项目都是 StarRocks。之前写 `UPDATE dim.dim_user_all dua SET ... FROM ... WHERE dua.xxx = ...` 这种给目标表加别名的语法，在 StarRocks 上会报 "Unexpected input 'dua'" 语法错误（StarRocks UPDATE 的目标表不支持别名，WHERE 里要用未限定的表名引用目标）。

**How to apply:**
- 写 UPDATE / INSERT / MERGE / DDL / 函数 / hint / 分区属性时，默认按 StarRocks 语义来
- 对有疑问的语法（如 UPDATE FROM、窗口函数、特定 UDF、BITMAP/HLL 用法、动态分区、PK 表 upsert 语义）先确认 StarRocks 是否支持
- 具体已知约束：
  - `UPDATE table_name` 目标表**不能加别名**；WHERE 里用 `table_name.col` 或不加表名限定引用目标
  - StarRocks 3.1+ 才支持 `UPDATE ... FROM`，仅适用于主键表（Primary Key table）
  - 主键表用 `INSERT INTO` 即是 upsert
  - `INSERT OVERWRITE ... PARTITION (pYYYYMMDD)` 是原子替换分区的标准写法
- 不确定时，宁可先在 `.claude/database/` 元数据/剧本里查证或先跑 dry-run 验证，不要直接抛给用户去踩错
