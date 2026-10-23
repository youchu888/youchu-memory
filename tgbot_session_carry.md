# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-23 · 最新归档：`sessions/tg-rotate-2026-10-23-1610.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 上游缺表时**不要只修 snap 或 SR DDL**；应 **spark-sql 实查 prod Paimon 表是否存在**，并对照 prod/test 编排是否含该任务。
- 三表 SR 正式表 **主键与 `ad004aed` 不一致时禁止 ALTER**，须 **DROP + CREATE**；部门周/月现网 0 行可直重建；**产品周等有历史行**（如约 799 行）须先确认**新粒度会清空**，再交运维执行。
- agent-bus：**60s 内 ACK**；若 ACK 被 silent/dedup 丢掉，用 `agent_bus_send.py` **`--no-dedup` 重发**，勿当已 ack；干完再 **reply 结案**。
- [LESSON: mgmt-report,prod-gate|三表挂 prod 前先查 prod Paimon 是否存在 `ads_channel_metrics_daily_d` 及编排步，缺则先走完并审发 013，勿只修 snap/SR]
- [LESSON: sr-ddl,mgmt-report|Spark 三表 SR 主键与 ad004aed 不一致必须 DROP 重建；有历史数据的表须先确认清空后再让运维执行]
- 汇报「渠道维已有数」须拆两层：**SR `dim.dim_channel_info_all` 本体行数** vs **Paimon `dim_channel_info_all_snap` 分区/行数**；本体有数不代表 00 槽 snap 已出，后者仍可能 0 行/无分区。
- 通知发版进度前：**prod 只读核水位**（SR 行数 + snap 状态），再经 agent-bus 转告，并明确问「代发到哪一步、是否先跑 snap / 先发后有数再重跑」。
- 管理报表三表 Spark 版（`ad004aed`）改读 **`paimon.dim.dim_channel_info_all_snap`（`snap_dt=DT`）**，去掉 srViews，加 **snap 水位探针**；提审/挂 prod 前须核 prod 快照 SQL（如历史 **减 8 小时** 时区处理已去掉）。
- 三表挂生产的**真正上游**往往是 **`ads.ads_channel_metrics_daily_d`**：三表计算第一步探针/SQL 都依赖它；prod Paimon 无表会 `TABLE_OR_VIEW_NOT_FOUND`，且 prod 编排里可能没有对应步（test 常在 **09 槽 `g_ads_channel_metrics_daily_d`**）。
- **`dev-20261016-013`【渠道日指标】** 未审发前，三表即使 DDL/快照就绪也**不能**完整挂 prod；013 须 **S6 产物齐 → `request-publish`**，审发后再挂三表。
- 无 prod SR 写权限：DDL 打成运维包（如 `ops_system/spark_migrate/_ops_pack/prod_rebuild_mgmt_report_sr_three_tables_*.sql`），运维执行后请审核人 **`SHOW CREATE TABLE` 复核**，再继续生产 S7（建 Paimon 表 → 送 SQL → 挂编排 → 当天格补跑）。
- **知秋 2026-10-20 定调**：管理报表三表**不再上海豚、走 Spark**；`dev-20261013-001/002/003` 海豚会话须 **`withdraw-publish`**，新海豚发布申请一律不收；继续 **`dev-20261022-001/002/003` + `ad004aed`**。
- 推荐顺序：**013 审发 → 三表 SR DROP 重建（运维）→ snap/Paimon + prod 编排 → 补跑**；切 Spark 时在 **`wf_ads_日报表_日`** 停海豚侧三表任务（`ads_dept_promotion_summary_w/m`、`ads_product_promotion_summary_w`）。
- > **指令**：先读本文件里的未结事项。做到某件事时再 `lookup-rules.sh` 查对应规则，不要在启动时通读红线和经验。
- 管理报表三表：业务已确认「代码没问题」时，**不必等当日维表补数完成**即可按现行代码走生产发布。
- 维表当日补数属于并行安排：**先发任务 / 发版，补数完成后 snap 有数，再重跑依赖任务**即可闭环。
- 私聊放行（如私聊#577）与 agent-bus 回狂人应**语义一致**：先发、补数后重跑，避免狂人侧仍按「等维表」理解。
- 向狂人转达生产放行时，用 **`dolphin_prod` + 范围（三表）+ 补数后重跑** 一句说清，便于对方按海豚/补数节奏执行。

