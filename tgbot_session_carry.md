# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-25 · 最新归档：`sessions/tg-rotate-2026-07-25-1205.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 两条 DWS **禁止**把 page_stay 与五档时长硬并表：粒度（有无 uid）、主指标（valid_stay vs 墙钟五档）、典型用法（导出/对账 vs 看板柱状图）都不同；`division_alignment.md` 已划界「禁止重复聚合同一指标」
- 五档合表核心判别列：`stat_grain`（`session`=单次五档，`daily`=日均五档）；同名 `duration_bucket` 语义不同，查询/接口必须带 `WHERE stat_grain=...`
- test 改 PK/删表：`my.cnf.test` 的 dc_admin **对 dws 无 DROP**；建删表迁移用 **test root `@43.212.113.132:9030`（无密码）**，不要推给主人手工跑
- 仅 `CREATE IF NOT EXISTS` 无法给旧表加 `stat_grain` 进主键；结构变更必须 **DROP 旧表 → CREATE 新 DDL → 补分区 → 重跑 ETL**
- [LESSON: test_db|test 上 dws 删表/改 PK 用 root@43.212.113.132:9030，勿用 my.cnf.test 的 dc_admin 再推主人]
- [LESSON: duration_model|page_stay 是 uid×dt 事实表，session_duration 是多维预聚合；合表只动后者，禁止与 page_stay 并表]
- 项目里「时长」分两条线：`dws_user_page_stay_d`（页面停留/valid_stay）是 `dt+app_id+uid` 账户日事实表，维度列挂在 uid 行上，**不是**多维预聚合；`dws_session_duration_*`（PRD 五档）才是 `dt+切片维+duration_bucket` 的多维预汇总
- 用户说的「合表」指**五档线内部** 4 张 → 2 张（账号/设备各一张），不动 `dws_user_page_stay_d`
- 合表 ETL 用两段 `SELECT UNION ALL` 写同一张表，**不能**一条 SQL 混算 session 与 daily，上游聚合逻辑不同
- 统一统计字段：账号侧 `session_cnt/user_cnt/duration_sum_sec/bounce_cnt`；设备侧 `device_cnt` 替代 `user_cnt`；均值拆成 `avg_session_duration_sec`（仅 session 行）和 `avg_daily_duration_sec`（仅 daily 行），不用泛化 `avg_duration_sec`
- session 分支验数口径：`(is_valid=1 OR duration_bucket=0)`；bounce 走 `duration_bucket=0`，不单独开维
- 合表后废弃：`dws_session_daily_user_d`、`dws_session_daily_device_d`（DDL/SQL/task 标 deprecated）；海豚需停用对应 daily task
- 合表完成后验数：按 `stat_grain` 分行核对 session_cnt/user_cnt(device_cnt)/bounce_cnt，与合并前两表合计一致（例 dt=2026-07-24）
- 群聊问进度：**第一句给结论**（如「还在对齐、两边都还没首跑」），再补 2~4 条 `·` 列点，别铺表格和 `##`
- 回群进度前**先核对 bus 实际进展**（如 bus#5471 / checkpoint 回执），勿凭记忆或草稿状态报
- 验数/派活若 bus 写明「结论请回 bus」→ **验完直接 agent-bus reply 结案**，群里 @ 提问者一句带过即可
- 群聊你是 **初儿**（`@youchu_ai_bot`）；**禁止**让同事 `@又初`；结尾固定「有疑问 @worker_ant_bot 或 @youchu_ai_bot」
- [LESSON: paimon-shadow|影子压测用独立 Spark wf + `_shadow` 表，源侧对齐后再首跑，严禁动现网 SR]

