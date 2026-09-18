# 大漏斗 sandbox explain 回执 · bus#7859

- 集群：hadoop-1 · `run_test.sh`（禁 run_step_once）
- steps：`/home/ec2-user/pipeline-runner/steps/test_big_funnel.json`
- SQL：pipeline-runner/sql/`dws_app_event_funnel_d_d_daily_stage_{metrics,wide}.sql`
- 参数：`--dt=2026-09-02 --hh=00 --explain`（day unit → 数据段 slot=`2026-09-01`）
- OUT_DB=`test.dws` · app_filter_* 空串

## 结果

| step | exit | EXPLAIN INSERT | 备注 |
|------|------|----------------|------|
| dws_app_event_funnel_metric_stg_d | 0 | OK ~454s | CREATE DB/TABLE 过；Physical Plan 产出 |
| dws_app_event_funnel_d_d | 0 | OK ~1.4s | Pushed Filters: EqualTo(dt,2026-09-01) |

日志：
- `.../logs/big_funnel_explain_metrics_20260903_092827.log`
- `.../logs/big_funnel_explain_wide_20260903_093719.log`

## 隐性点（供你看）

1. **分区裁剪**：metrics/wide 的 V2ScanRelationPushDown 均见 `EqualTo(dt,2026-09-01)`，事件源侧裁剪在。
2. **metrics 计划偏重**：explain 阶段反复 `PaimonScan splits≈12527`（约 7.5min 才出计划）。主因是 SQL 多路 UNION + 每 metric 分支重复挂 `user_is_new`（四路 day_uids ∪ register），计划扇出大；不是建表失败。
3. **类型**：`e.dt = DATE '${DT}'` 与 `v/n/c.dt = '${DT}'` 混用 DATE/字符串，计划里对 dw 事件有 `cast(dt as string)`；当前能过 analyze，真跑前可统一成一种以免隐式 cast。
4. **wide**：读 stg 的 pushdown 干净，无额外类型警告。

未做真写（仅 --explain）。要 SF-81 真跑再说一声。
