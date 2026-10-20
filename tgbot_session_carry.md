# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-20 · 最新归档：`sessions/tg-rotate-2026-10-20-1708.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- [LESSON: spark_migrate|dim|paimon|SR 维表无 dt 列时禁止抄 dim_app_info_all 的 dt 分区，改用 *_snap + snap_dt=${DT}，并对齐 844c4baf/_snap 样板]
- [LESSON: datacheck|dim|prod SR 维表 0 行时 Paimon 空 snap_dt 分区先判源表是否真无数据，勿当同步逻辑故障]
- SR 维表同步 Paimon 先分两类：源表**自带按日 `dt` 全量**→照 `dim_app_info_all`（`PARTITIONED BY (dt)`，只搬 `dt=${DT}`）；源表**无 `dt`、会变配置**→照 `*_snap`（`snap_dt=${DT}` 日快照留历史）。
- `dim.dim_channel_info_all` 无 `dt`，Paimon 表名/口径用 **`dim_channel_info_all_snap`**，分区 **`snap_dt`**，主键 **`(snap_dt, id)`**。
- 样板链：bus#10789 / commit **`844c4baf`**（测试集群已跑通）；渠道维对齐后落 **`ops_system/spark_migrate/dim_channel_info_all/`**（DDL / ETL / step / 文档）。
- **ETL 只做 `INSERT OVERWRITE` 当天分区**，不在 ETL 里 `CREATE`；建表 DDL 单独文件，交集群侧建表、挂 **`full_chain` 00 槽 timer**。
- 同步 SQL 结构：**`timer` + `srViews`**（如 `sr_dim_channel`）；`created_at` / `updated_at` 从 SR 读出后 **减 8 小时** 再写入 Paimon。
- 下游 Spark（渠道周/月/部门等）JOIN 维表时统一 **`WHERE snap_dt = '${DT}'`**，与快照分区一致。
- 新链路 **`dbprogramming` 须建 dev session**（例 `dev-20261020-001`），本地产物与平台 session 同步推进，不单机搓 SQL。
- **职责切分**：又初 = session + 同步稿 + test 可对账材料；**建 Paimon 表 / 挂编排 / 灌种 / 沙箱对账** 归知秋（狂人）侧。
- test SR 有样例行（如约 20 行）可验逻辑；**prod SR 当前 0 行** → 同步写出**空分区属源空**，部门等列空≠ ETL 写错。
- 用户明确要求再 **commit/push**；交付 commit 例 **`dd5738d4`**（feat(dim): 渠道维表 SR→Paimon 日快照同步稿）。
- 提交前若 **stash 与无关 WIP（如广告层）冲突**，先还原无关改动，只推本任务目录，避免混进别的 diff。
- agent-bus：**60s 内 ACK**，干完 **reply 结案**；ACK 偶发 silent 丢包时，以带实质内容的 **reply**（如 #10790）为准。
- 列有、任务不写**：先四路对照——表结构（test/prod）、仓库 SQL/DDL、海豚 live SQL、同批相邻 task；常见根因是 **DDL 已落、含新列 ETL 未发 live**，不是「仓库没写」。
- session MCP 写 stage 失败**：用开发平台 **`PUT …/full` 合并 state** 再提审，勿空标 stage。
- 渠道日指标 P0**：`ads_channel_metrics_daily_d`（`wf_ads_日报表_日` / `dev-20261016-013`）提前；视频段从 dwd 改为读 behavior 宽表，影子验证 PASS 再切。
- [LESSON: video-migration,paimon,dwd|视频 ADS/日报改源优先 dwm 用户视频中间表，缺列先商量；未迁完 dwd 读明细任务前禁止停拆事件慢 task。]

