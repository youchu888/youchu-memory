---
date: 2026-09-24
tags: [spark, OUT_DB, pipeline-runner, ops_system, paimon]
severity: high
domain: ops
---

# Spark 写目标只许 `${OUT_DB}.<层>.<表>`（OUT_DB 只装 catalog）

## 背景

知秋 2026-09-24 钦定并已上生产（bus#9225）：`${OUT_DB}` 语义从「完整库名」改为「仅 catalog」；层库写死在 SQL 里。生产 OUT_DB=`paimon`，验证 OUT_DB=`test`。

## 坑 / 错误做法

- `INSERT OVERWRITE dws.xxx`（裸库名靠 defaultCatalog）
- `INSERT OVERWRITE paimon.dws.xxx`（写死 catalog）
- `INSERT OVERWRITE ${OUT_DB}.xxx`（旧：OUT_DB=paimon.dws）
- 往 `full_chain.json` / steps 的 `params.render` 写 `OUT_DB`（conf 统一给，写了也没用；steps.outDb 留空会启动报错）
- 改 FROM/JOIN 读侧去跟验证 catalog（验证要读生产真数据）
- `sr_sql` 回写套 `${OUT_DB}`（会打到 paimon，应写 SR 影子表）
- 新 SQL 再放 `pipeline-runner/sql/`；同一份 SQL 多处复制

## 正确做法

```sql
CREATE DATABASE IF NOT EXISTS ${OUT_DB}.dws;
CREATE TABLE IF NOT EXISTS ${OUT_DB}.dws.dws_xxx_d_d (...);
INSERT OVERWRITE ${OUT_DB}.dws.dws_xxx_d_d
```

- 新代码路径：`ops_system/<层>/<任务名>/spark/sql/xxx.sql`
- 读侧一字不动；`sr_sql` 不套 OUT_DB
- 改未提交 SQL 前先 `git pull`，避免与已上线 38 份新写法打架
- 剩余 58 份归位 + full_chain 路径改写等知秋定停机窗口，未到点不擅自大改生产路径

## 验证

渲染后应为 `paimon.dwm.xxx` / `test.dws.xxx` 这种三层名；槽位真跑零 ERROR（先例：槽位 16 → `paimon.dwm.dwm_user_video_behavior_d`）。

## 关联

- bus#9225（狂人广播）
- feedback：`feedback_spark_OUT_DB_catalog_only.md`
- 回滚点：各文件 `.bak_outdbspec_20260924`；归档死文件 `/home/ec2-user/spark/_archive_20260924/`
