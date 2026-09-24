# Spark · OUT_DB 只装 catalog（知秋 2026-09-24）

写新 Spark SQL / 改写目标时：

1. **只许** `${OUT_DB}.<层>.<表>`（层 = dwm/dws/ads/dim/dwd…）
2. **禁止** 裸库名、写死 `paimon.`、旧式 `${OUT_DB}.表`
3. **OUT_DB** 由 conf 统一给；不要往 `full_chain.json` `params.render` 塞 OUT_DB
4. **读侧**（FROM/JOIN）不动；**sr_sql** 不套 OUT_DB
5. **新文件**只落 `ops_system/<层>/<任务>/spark/sql/`；勿再往 `pipeline-runner/sql/` 加新文件、勿多处复制同一份 SQL

lesson：`lessons/2026-09-24-spark-OUT_DB只装catalog-写目标须三层名.md`
