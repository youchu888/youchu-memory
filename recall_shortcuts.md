# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 07 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-07-25-page_stay-是-uid-dt-事实表-session_duration-是多维预聚合-合.md` | 2026-07-25-page_stay-是-uid-dt-事实表-sessio |
| ## 07 113 132 2026 212 | `~/.dc-platform/memory/lessons/2026-07-25-test-上-dws-删表-改-pk-用-root-43-212-113-132-9030-勿用.md` | 2026-07-25-test-上-dws-删表-改-pk-用-root-43- |
| ## 07 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-07-25-五档-dws-合表用-stat_grain-区分单次-日均-查询必带该列-否则两种-y-轴会混算.md` | 2026-07-25-五档-dws-合表用-stat_grain-区分单次-日均 |
| daily deprecated） dws_session_daily_devi | `sessions/tg-rotate-2026-07-25-1205.md` | 合表后废弃：`dws_session_daily_user_d`、`dws_se |
| bounce duration_bucket is_valid or sessi | `sessions/tg-rotate-2026-07-25-1205.md` | session 分支验数口径：`(is_valid=1 OR duration_ |
| avg_daily_duration_sec avg_duration_sec  | `sessions/tg-rotate-2026-07-25-1205.md` | 统一统计字段：账号侧 `session_cnt/user_cnt/duratio |
| all daily etl select session sql | `sessions/tg-rotate-2026-07-25-1205.md` | 合表 ETL 用两段 `SELECT UNION ALL` 写同一张表，**不能 |
| dws_user_page_sta dws_user_page_stay_d 「 | `sessions/tg-rotate-2026-07-25-1205.md` | 用户说的「合表」指**五档线内部** 4 张 → 2 张（账号/设备各一张），不 |
| +d +切 _b _s al at | `sessions/tg-rotate-2026-07-25-1205.md` | 项目里「时长」分两条线：`dws_user_page_stay_d`（页面停留/ |
| duration_model lesson page_stay session_ | `sessions/tg-rotate-2026-07-25-1205.md` | [LESSON: duration_model/page_stay 是 uid× |
| 90 9030 dc_admin dws lesson my.cnf.test | `sessions/tg-rotate-2026-07-25-1205.md` | [LESSON: test_db/test 上 dws 删表/改 PK 用 ro |
| create ddl dr drop etl exists | `sessions/tg-rotate-2026-07-25-1205.md` | 仅 `CREATE IF NOT EXISTS` 无法给旧表加 `stat_gr |
| 9030 @43.212.113.132 dc_admin drop dws m | `sessions/tg-rotate-2026-07-25-1205.md` | test 改 PK/删表：`my.cnf.test` 的 dc_admin ** |
| ... daily dura duration_bucket session s | `sessions/tg-rotate-2026-07-25-1205.md` | 五档合表核心判别列：`stat_grain`（`session`=单次五档，`d |
| _s al ay d_ division_alignment.md dws | `sessions/tg-rotate-2026-07-25-1205.md` | 两条 DWS **禁止**把 page_stay 与五档时长硬并表：粒度（有无  |
| ## 07 2026 25 agent_session_rotate attri | `~/.dc-platform/memory/lessons/2026-07-25-归因-shadow-读-paimon-register-landing-click-view-开.md` | 2026-07-25-归因-shadow-读-paimon-register-l |
| ## 07 2026 25 agent_session_rotate bus | `~/.dc-platform/memory/lessons/2026-07-25-群聊进度第一句给结论-回前核对-bus-实态-列点-4-条用-验完-bus-结案再群里一句带过.md` | 2026-07-25-群聊进度第一句给结论-回前核对-bus-实态-列点-4-条 |
| ## 07 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-07-25-影子压测用独立-spark-wf-_shadow-表-源侧对齐后再首跑-严禁动现网-sr.md` | 2026-07-25-影子压测用独立-spark-wf-_shadow-表-源侧 |
| 一眼 人扫 列点 可长 就懂 扫一 | `sessions/tg-rotate-2026-07-25-0601.md` | 群聊列点**最多 4 条**；私聊可长，群里让人扫一眼就懂 |
| bus landing spark 一步 下一 下一步动作 | `sessions/tg-rotate-2026-07-25-0601.md` | 卡点要写清：**谁在等什么**（A 等 Spark 骨架；B 等 landing |
| ping wf 分工 双线 双线分工后进度口径 口径 | `sessions/tg-rotate-2026-07-25-0601.md` | 双线分工后进度口径：各报 **wf 名 + 预计开跑时间**；首跑后互 ping |
| bus click landing paimon register shadow | `sessions/tg-rotate-2026-07-25-0601.md` | `B` 线归因 shadow 源读 Paimon 的 register + la |
| shadow spark sr wf 不动 不动现网 | `sessions/tg-rotate-2026-07-25-0601.md` | Shadow 压测走 Spark 另起链路，**不动现网 SR**；表名带 `_ |
| _p _压 _用 ai f_ im | `sessions/tg-rotate-2026-07-25-0601.md` | Paimon 影子压测双线：`A`=`paimon.dim.dim_user_d |
| bus group lesson tg ≤4 一句 | `sessions/tg-rotate-2026-07-25-0601.md` | [LESSON: tg-group/群聊进度第一句给结论，回前核对 bus 实态 |
| lesson paimon shadow spark sr wf | `sessions/tg-rotate-2026-07-25-0601.md` | [LESSON: paimon-shadow/影子压测用独立 Spark wf  |
| @work @worker_ant_bot @youchu_ai_bot @yo | `sessions/tg-rotate-2026-07-25-0601.md` | 群聊你是 **初儿**（`@youchu_ai_bot`）；**禁止**让同事  |
| agent bus bus」→ reply 「结 一句 | `sessions/tg-rotate-2026-07-25-0601.md` | 验数/派活若 bus 写明「结论请回 bus」→ **验完直接 agent-bu |
| bus bus#5471 checkpoint 先核对 凭记 勿凭 | `sessions/tg-rotate-2026-07-25-0601.md` | 回群进度前**先核对 bus 实际进展**（如 bus#5471 / check |
| ## 2~4 「还 」） 一句 两边 | `sessions/tg-rotate-2026-07-25-0601.md` | 群聊问进度：**第一句给结论**（如「还在对齐、两边都还没首跑」），再补 2~4 |
| ## 07 2026 24 agent agent_session_rotate | `~/.dc-platform/memory/lessons/2026-07-24-跨-agent-分工对齐走-bus-互督-checkpoint-不在群里公开回复派活细节.md` | 2026-07-24-跨-agent-分工对齐走-bus-互督-checkpoi |
| ## 07 2026 24 agent_session_rotate all | `~/.dc-platform/memory/lessons/2026-07-24-归因-apply-须同步回写-dim_user_daily_snapshot-t-1-分区-ch.md` | 2026-07-24-归因-apply-须同步回写-dim_user_daily |
| ## 07 2026 24 agent_session_rotate atten | `~/.dc-platform/memory/lessons/2026-07-24-查岗-handler-未命中须打-debug-日志-触发条件收成-抽查群-即尝试解析-勿依赖固定.md` | 2026-07-24-查岗-handler-未命中须打-debug-日志-触发条 |
| dim is_rewrite_channel is_run organic re | `sessions/tg-rotate-2026-07-24-2111.md` | **回写开关与条件**：`is_run=1` 才算归因；`is_rewrite_ |
| apply channel_appl channel_apply dim.cha | `sessions/tg-rotate-2026-07-24-2111.md` | **归因回写顺序**：`dim_user_all` 构建 → `result_d |
| 15（early）+ 50（full） @0 @00 @04 _d | `sessions/tg-rotate-2026-07-24-2111.md` | **快照调度**：早窗 `wf_用户日快照_日` @00:15（early）+  |
| 002 20260713 23 app_id dev dim.dim_user_ | `sessions/tg-rotate-2026-07-24-2111.md` | **用户日增量表**：`dim.dim_user_daily_snapshot` |
| .env end false set_leave_day.py tg_work_ | `sessions/tg-rotate-2026-07-24-2111.md` | **绿点配置入口**：`.env` 的 `TG_WORK_ONLINE_STAR |
| 09 22 30 30–22 45s com.youchu.tg | `sessions/tg-rotate-2026-07-24-2111.md` | **TG 绿点保活**：`com.youchu.tg-work-online`  |
| all apply attribution channel dim dim_us | `sessions/tg-rotate-2026-07-24-2111.md` | [LESSON: attribution,dim/归因 apply 须同步回写  |
