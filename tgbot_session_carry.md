# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-20 · 最新归档：`sessions/tg-rotate-2026-10-20-2308.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主人说「上传云端」时：以当日已定稿 `reports/日报-YYYY-MM-DD.md` 为准，**改字后再传**；未指定日期用当天。
- agent-bus `mode=work`：同一 Cursor 主会话处理，**60 秒内先 ACK**，干完再 **reply** 才结案；reply 成功前不要 `mark_processed`。
- S5 开放后的执行姿态：在平台内对指定 session **自己做 S5**，不要另找绕路（test 假跑、手改 prod 等）。
- [LESSON: dev-platform|S5|stage5|prod-dryrun|知秋定案|2026-10-20|008-012|019|开发者可在生产调度器自送 SQL 跑 S5；禁止覆盖生产在跑步正在用的 SQL 文件；申请发布须 S1～S6 全部完成]
- [LESSON: agent-bus|ack|silent|no-dedup|ACK 可能被 silent 丢弃时用 --no-dedup 重发；结案与对账以 reply 为准，勿因 ACK 未镜像而重复整单]
- 上传前先确认本地定稿文件存在，再跑 `python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`。
- 上传成功以 API 回执为准（如 `status=inserted`、记录 ID）；对话里报结果即可，不必再贴全文（防与 TG 双份）。
- ACK 可能被服务端 **silent 吞掉**（去重/静默策略）；若需确保对方看到，可用 `agent_bus_send.py --no-dedup` 重发 ACK，**以 reply 为结案依据**。
- 平台政策类派单：除 reply 外应同步 **MEMORY_OPEN**（删过时 HOLD/闸）并 **增补 lesson**，避免下次仍按旧闸执行。
- **S5 生产验证已对开发者开放**（知秋定案，约 2026-10-20 22:3x 北京）：相关 session（摘录中为 008～012、019）可自行把 SQL 送到**生产调度器**跑 S5。
- S5 唯一硬限制：**生产正在跑的那一步所引用的 SQL 文件不可覆盖**；平台会提示走正式发布，不能硬改在用文件。
- 申请发布新规矩：**S1～S6 全部完成**后才能申请发布（与 S5 开放并行，提审前仍要齐 stage 产物）。
- [LESSON: spark_migrate|dim|paimon|SR 维表无 dt 列时禁止抄 dim_app_info_all 的 dt 分区，改用 *_snap + snap_dt=${DT}，并对齐 844c4baf/_snap 样板]
- [LESSON: datacheck|dim|prod SR 维表 0 行时 Paimon 空 snap_dt 分区先判源表是否真无数据，勿当同步逻辑故障]
- SR 维表同步 Paimon 先分两类：源表**自带按日 `dt` 全量**→照 `dim_app_info_all`（`PARTITIONED BY (dt)`，只搬 `dt=${DT}`）；源表**无 `dt`、会变配置**→照 `*_snap`（`snap_dt=${DT}` 日快照留历史）。
- `dim.dim_channel_info_all` 无 `dt`，Paimon 表名/口径用 **`dim_channel_info_all_snap`**，分区 **`snap_dt`**，主键 **`(snap_dt, id)`**。
- 样板链：bus#10789 / commit **`844c4baf`**（测试集群已跑通）；渠道维对齐后落 **`ops_system/spark_migrate/dim_channel_info_all/`**（DDL / ETL / step / 文档）。
- **ETL 只做 `INSERT OVERWRITE` 当天分区**，不在 ETL 里 `CREATE`；建表 DDL 单独文件，交集群侧建表、挂 **`full_chain` 00 槽 timer**。

