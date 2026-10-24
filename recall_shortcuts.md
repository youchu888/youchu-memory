# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 10 2026 24 ads_dept_promotion_summary | `~/.dc-platform/memory/lessons/2026-10-24-ddl-dolphin-半上线-主键变更.md` | 2026-10-24-ddl-dolphin-半上线-主键变更 |
| live l— prod ql sq sql——环境间不能假设「一起升了」 | `sessions/tg-rotate-2026-10-24-1011.md` | **prod 海豚 vs test 海豚可能不同步**：摘录中 prod liv |
| ... 05.ads live max ops_system paid_type | `sessions/tg-rotate-2026-10-24-1011.md` | **test 典型错配**：表半改（加列未换 PK），海豚 live 仍 **渠 |
| channel dim_channel_info_all paid_type p | `sessions/tg-rotate-2026-10-24-1011.md` | **prod 典型错配**：海豚 task 已按新列写（无 `channel`、 |
| add alter column drop ×是 ×部 | `sessions/tg-rotate-2026-10-24-1011.md` | **主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER |
| alter channel ddl dept_id month_start_dt | `sessions/tg-rotate-2026-10-24-1011.md` | **只 ALTER 加列 ≠ 换主键落地**：现网 PK 仍是 `(month_ |
| ads_dept_promotion_summary_m channel dep | `sessions/tg-rotate-2026-10-24-1011.md` | **`ads_dept_promotion_summary_m` 目标粒度**： |
| ddl live pk prod spark sql | `sessions/tg-rotate-2026-10-24-1011.md` | **半上线判定**：改口径表要同时核对「仓库 DDL/SQL、海豚 live S |
| ads_dept_promotion_summary_m alter creat | `sessions/tg-rotate-2026-10-24-1011.md` | [LESSON: ads_dept_promotion_summary_m/dd |
| 10 20 checklist ddl etl insert | `sessions/tg-rotate-2026-10-24-1011.md` | 与 10-20 同类根因**：**DDL/改表与写表 ETL 未同批对齐**；发 |
| canonical create ddl etl live pk | `sessions/tg-rotate-2026-10-24-1011.md` | 交付物要对齐三件套**：交给运维的 DDL、海豚发布 SQL、仓库 canoni |
| 1023.sql ddl pk ×部 「渠 「给 | `sessions/tg-rotate-2026-10-24-1011.md` | 运维建表脚本要回读原文**：群里的 **`1023.sql` 若按「渠道×部门」 |
| add alter column drop ×是 ×部 | `sessions/tg-rotate-2026-10-24-1011.md` | 主键/粒度变更必须 DROP 重建（或等价换表）**：不能指望 `ALTER A |
| ## 10 2026 23 ad004aed agent_session_rot | `~/.dc-platform/memory/lessons/2026-10-23-spark-三表-sr-主键与-ad004aed-不一致必须-drop-重建-有历史数据的表须先.md` | 2026-10-23-spark-三表-sr-主键与-ad004aed-不一致必 |
| ## 10 2026 23 ack agent | `~/.dc-platform/memory/lessons/2026-10-23-ack-无可见回执时用-agent_bus_send-py-no-dedup-重发.md` | 2026-10-23-ack-无可见回执时用-agent_bus_send-py |
| ## 013 10 2026 23 ads_channel_metric | `~/.dc-platform/memory/lessons/2026-10-23-三表挂-prod-前先查-prod-paimon-是否存在-ads_channel_metric.md` | 2026-10-23-三表挂-prod-前先查-prod-paimon-是否存在 |
| 001 002 003 10 20 2026 | `sessions/tg-rotate-2026-10-23-1610.md` | **知秋 2026-10-20 定调**：管理报表三表**不再上海豚、走 Spa |
| .sql 7（ create ddl ops_pac ops_pack | `sessions/tg-rotate-2026-10-23-1610.md` | 无 prod SR 写权限：DDL 打成运维包（如 `ops_system/sp |
| 013 20261016 ddl dev prod publish | `sessions/tg-rotate-2026-10-23-1610.md` | **`dev-20261016-013`【渠道日指标】** 未审发前，三表即使  |
| 09 ads.ads_channel_metrics_daily_d es g_ | `sessions/tg-rotate-2026-10-23-1610.md` | 三表挂生产的**真正上游**往往是 **`ads.ads_channel_met |
| ad004aed dt l（ paimon.dim.dim_channel_in | `sessions/tg-rotate-2026-10-23-1610.md` | 管理报表三表 Spark 版（`ad004aed`）改读 **`paimon.d |
| agent bus prod snap 「代 一步 | `sessions/tg-rotate-2026-10-23-1610.md` | 通知发版进度前：**prod 只读核水位**（SR 行数 + snap 状态）， |
| 00 dim.dim_channel_info_all dim_channel_ | `sessions/tg-rotate-2026-10-23-1610.md` | 汇报「渠道维已有数」须拆两层：**SR `dim.dim_channel_inf |
| ad004aed ddl drop lesson mgmt report | `sessions/tg-rotate-2026-10-23-1610.md` | [LESSON: sr-ddl,mgmt-report/Spark 三表 SR  |
| 013 ads_channel_metrics_daily_d gate les | `sessions/tg-rotate-2026-10-23-1610.md` | [LESSON: mgmt-report,prod-gate/三表挂 prod  |
| 60s ack agent agent_bus agent_bus_send.p | `sessions/tg-rotate-2026-10-23-1610.md` | agent-bus：**60s 内 ACK**；若 ACK 被 silent/d |
| 799 ad004aed alter create drop sr | `sessions/tg-rotate-2026-10-23-1610.md` | 三表 SR 正式表 **主键与 `ad004aed` 不一致时禁止 ALTER* |
| ddl paimon prod snap spark sql | `sessions/tg-rotate-2026-10-23-1610.md` | 上游缺表时**不要只修 snap 或 SR DDL**；应 **spark-sq |
| ## 10 2026 23 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-23-私聊拍板与回狂人正文须同口径-先发-补数后重跑-避免双通道说法不一致.md` | 2026-10-23-私聊拍板与回狂人正文须同口径-先发-补数后重跑-避免双通道 |
| ## 10 2026 23 agent agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-23-代码已确认且业务口头放行时三表可先-prod-发布-维表当日补数-snap-有数后再重跑任务-b.md` | 2026-10-23-代码已确认且业务口头放行时三表可先-prod-发布-维表当 |
| 「先发 不是 不是跳过验数 代码 侧已 前提 | `sessions/tg-rotate-2026-10-23-1209.md` | 此类放行属于 **「先发 + 补跑」** 策略，不是跳过验数；前提是代码侧已核对 |
| #1 11 12 25 3） 53 | `sessions/tg-rotate-2026-10-23-1209.md` | 回 bus 时带上 **bus#**（如 bus#11253）和 **reply |
| agent_bus_send.py dedup no 再次 出站 出站若被 | `sessions/tg-rotate-2026-10-23-1209.md` | 出站若被 **去重拦截**，在确属需再次送达（非误触重复）时，用 `agent_ |
| dolphin_prod 一句 一句说清 三表 于对 产放 | `sessions/tg-rotate-2026-10-23-1209.md` | 向狂人转达生产放行时，用 **`dolphin_prod` + 范围（三表）+  |
| #5 57 77 7） agent bus | `sessions/tg-rotate-2026-10-23-1209.md` | 私聊放行（如私聊#577）与 agent-bus 回狂人应**语义一致**：先发 |
| snap 于并 任务 依赖 先发 先发任务 | `sessions/tg-rotate-2026-10-23-1209.md` | 维表当日补数属于并行安排：**先发任务 / 发版，补数完成后 snap 有数，再 |
| 「代 」时 三表 不必 不必等当日维表补数完成 业务 | `sessions/tg-rotate-2026-10-23-1209.md` | 管理报表三表：业务已确认「代码没问题」时，**不必等当日维表补数完成**即可按现 |
| lookup rules.sh 不要 不要在启动时通 不要在启动时通读红线和经验 | `sessions/tg-rotate-2026-10-23-1209.md` | > **指令**：先读本文件里的未结事项。做到某件事时再 `lookup-rul |
| ## +金 10 2026 22 agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-22-重生成须先双机同步-金样实活核对-定稿后推-tg-云端仅在你明确要求时用定稿原样上传.md` | 2026-10-22-重生成须先双机同步-金样实活核对-定稿后推-tg-云端仅在 |
| ## 10 2026 22 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-22-对外回复禁用-主人-一律用-你-内部可留出处词-输出必须剥离.md` | 2026-10-22-对外回复禁用-主人-一律用-你-内部可留出处词-输出必须剥 |
