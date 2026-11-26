# 规则目录（自动生成 2026-11-26 22:50）

> 一行一条。启动扫目录；对上再 Read 原文。禁止整库灌进对话。

| 标签 | 一句话 | 文件 |
|------|--------|------|
| pinned-1 | **prod 海豚/写库不自发** — 须审核人（狂人/知秋等）；默认只做 test。 | `PINNED.md` |
| pinned-2 | **禁止改插件 version / 自打自装 vsix** — 只报 bug；官方包由野花下发。 | `PINNED.md` |
| pinned-3 | **已定规矩先确认再改** — feedback/rules 破例须用户明确说「改」。 | `PINNED.md` |
| pinned-4 | **提交即 push** — 说入库/commit 成功后立刻 `git push`（除非用户禁止）。 | `PINNED.md` |
| pinned-5 | **产出物互斥+换轨** — 先判定 commit/日报/bus/群进展只跟对应专条；commit 必须从 git diff 从零写（禁粘 b… | `PINNED.md` |
| pinned-6 | **Dev Session 1–6 禁空标 done** — 每 stage 要有产物与证据；stage7 等审核。 | `PINNED.md` |
| pinned-7 | **datacheck 默认只查 T-1** — 用户未指定日期禁止扫多日。 | `PINNED.md` |
| pinned-8 | **agent-bus：秒回执可短，结案必须写出实际做了什么** — ACK 保持原样；后面追加一条列出查了哪/改了哪/贴了什么；禁只回「已知… | `PINNED.md` |
| pinned-9 | **固定流程先跑 runbook** — 归因/补数等禁止对话里从零造轮子。 | `PINNED.md` |
| pinned-10 | **INSERT 必须显式列名** — 防列错位（尤其加列后）。 | `PINNED.md` |
| pinned-11 | **StarRocks：禁 `$[yyyyMMdd]` 类宏进直连 SQL** — 用字面量或会话变量。 | `PINNED.md` |
| pinned-12 | **核查认可后写回 playbook** — lesson 记坑；playbook 记可跑步骤。 | `PINNED.md` |
| pinned-13 | **工作簿/进展禁模板** — 收到点名后必须先实查（探针+cutoff work-log），口径截至汇报前；禁抄任务板套话；只 bus 回狂… | `PINNED.md` |
| pinned-14 | **群聊仅显式 @初儿/@又初 才回** — 裸喊名/探活收条不回。 | `PINNED.md` |
| pinned-15 | **日报：已完成+通俗书面；「上传云端」=填报 HTML/API，与 TG 无关** — 禁 bus#；云端用 `upload_work_re… | `PINNED.md` |
| pinned-16 | **健壮性优先** — 失败可自愈、不滚雪球、改完当场 smoke。 | `PINNED.md` |
| pinned-17 | **记忆：沉前查重；日常 append；勿用 upsert 当 append**。 | `PINNED.md` |
| pinned-18 | **记忆召回：动前先查；打开≠用了；真改做法才 touch**。 | `PINNED.md` |
| pinned-19 | **冷启动别只看 hot** — 必须同时看「按时间最近动过」。 | `PINNED.md` |
| pinned-20 | **提交范围** — 默认只动 `ops_system` 等业务目录；禁擅自改平台插件/api_v1。 | `PINNED.md` |
| pinned-21 | **TG 禁「这个回答合适吗？」** — SQL 答完禁止主动发满意/不满意按钮；纠错由用户主动说。 | `PINNED.md` |
| pinned-22 | **指令写明环境必须照办** — 说查 prod 就全程 prod；禁口称 prod、实查 test（或反过来）。 | `PINNED.md` |
| pinned-23 | **任务自主往下推** — 有下一步直接干；卡点 TG 私聊主人（并 bus 要材料），勿等主人追问「做完了吗」。 | `PINNED.md` |
| pinned-24 | **闲时沉淀、用时检索** — 收尾写 work-log/lesson；催日报/补活只读流水改稿并贴聊天，禁临时考古半仓。 | `PINNED.md` |
| pinned-25 | **git commit 说明用汉字** — 可 `feat(scope):` 前缀，冒号后必须中文；禁整段英文；钩子拦无汉字。 | `PINNED.md` |
| pinned-26 | **SR 按日分区建表必须带历史分区** — 默认 `history_partition_num=30` 且 `start=-10000`；禁… | `PINNED.md` |
| pinned-27 | **已定 runner 就只走 runner** — `run_test.sh` / daemon 槽位；禁框外串步、yarn 壳、海豚替跑，… | `PINNED.md` |
| pinned-28 | **可见文字不回头改历史** — 已提交的说明和文件不重写；此后新写的注释、文档、提交说明不要露出机器人痕迹。 | `PINNED.md` |
| pinned-29 | **对接文档只留最新一份** — 带日期的对接/变更稿不堆版本；新稿落地即删旧稿与跨目录副本。见 lesson `2026-09-16-对接文… | `PINNED.md` |
| pinned-30 | **做事要快** — 先结论、少探活、一题一会话；已知信息禁重猜重扫。见 `feedback_agent_speed.md`。 | `PINNED.md` |
| pinned-31 | **新增不改旧** — 新文件、新段落、新索引行可以直接加；改、删、重写已有句子先说明，等明确说「改」再动。 | `02.md` |
| pinned-32 | **共享组件故障禁止私自绕过** — 撞上 BitmapUdf / runner 公共路径 / Kryo 等共享层问题：只反馈，禁止改公共实现… | `03.md` |
| pinned-33 | **产发 bucket/并行度只认 prod 探数** — fanout/`_r`/Spark 上产前先查产线量级并对齐全网同类表；禁用 te… | `04-prod-bucket-probe.md` |
| pinned-34 | **缺 dwd_r 直接找斯科特** — 表结构/事件/bucket 私聊或群 @scott_188；禁止 bus 让狂人转。见 `feedb… | `05-dwd-r-direct-scott.md` |
| pinned-35 | **request-publish 前：禁冲掉 owned；归档须先 uncomplete** — `PUT /full` 必须合并保留 `d… | `06-request-publish-owned-archive.md` |
| pinned-36 | **全新业务直写正式表，禁影子双跑** — 无现网旧写方可对账时，pb/`countTable`/DDL/对接一律正式名；「影子 7 日对平」… | `07-new-biz-no-shadow-formal.md` |
| pinned-37 | **遇到的问题必须同会话沉淀成记忆** — 纠正/翻车/断链当场写 lesson（查重后 update 或新建）+ 索引；禁只认错、禁拖到闲时… | `08-problems-must-sediment.md` |
| pinned-38 | **新建 dwd_r 先评估再落表** — 跟业务确认、自估增量、定规模与分桶；`first-row` 默认不开，仅特殊场景保留第一条。见 `… | `09-dwd-r-new-eval.md` |
| pinned-39 | **给 worker_ant 发 bus：正文禁任何前缀标签，payload.kind 禁 reply/ack** — 勿写 `[REPLY]… | `39-bus-no-prefix-tags.md` |
| pinned-40 | **日报禁内部简写；自动定稿/wake 必须展开** — 勿写物化稿/影子/冒烟/对平/维/首灌/微差/七步等；old-mac 自动推与 ID… | `40-daily-report-no-abbrev.md` |
| pinned-41 | **对主人说话：英文技术词后必须括号跟中文** — 例 `wake（叫醒）`；细则 `feedback_youchu_gloss_englis… | `41-gloss-english-terms.md` |
| agent bus action items m | 狂人 bus 秒回执可短，结案必须追加实际做了什么 | `feedback_agent_bus_action_items_must_work.md` |
| agent bus all inbound mu | Feedback：收到的 bus 都要处理 · 另起执行（主人 2026-09-30） | `feedback_agent_bus_all_inbound_must_process.md` |
| agent speed | 做事要快（主人 2026-09-16 连纠） | `feedback_agent_speed.md` |
| always include event id  | 所有抽样明细数据都要带上 event_id 字段 | `feedback_always_include_event_id_in_samples.md` |
| analyze instruction env | 指令写明查 prod/test 时必须按该环境执行，禁止分析偏了或口说 prod、实查 test | `feedback_analyze_instruction_env.md` |
| attribution ua from dw a | For attribution analysis, user_agent must be sourced from dw.dw_user_… | `feedback_attribution_ua_from_dw_and_focus_ip.md` |
| board decisions detail | 拍板沟通：逐条展开 | `feedback_board_decisions_detail.md` |
| channel scoring query pa | 渠道评分表条件查询规则 | `feedback_channel_scoring_query_pattern.md` |
| commit message detailed | 提交说明尽量详细（主人 2026-10-30） | `feedback_commit_message_detailed.md` |
| commit no bus id | commit 说明禁 bus 编号 | `feedback_commit_no_bus_id.md` |
| confirm before breaking  | 已定规矩要破例：先确认再说改 | `feedback_confirm_before_breaking_rules.md` |
| daily report dual mac be | Feedback：日报必须先双机上传再同步再写（主人 2026-08-11） | `feedback_daily_report_dual_mac_before_2130.md` |
| daily report golden styl | 日报金样：以主人改定稿为准（又初必遵） | `feedback_daily_report_golden_style_from_owner_edits.md` |
| daily report human voice | 日报：说人话 + 条数灵活 + 禁止双推（主人 2026-08-28） | `feedback_daily_report_human_voice_no_dup_push.md` |
| daily report no abbrev e | 日报禁内部简写：自动推送与 IDE 同一标准 | `feedback_daily_report_no_abbrev_expand.md` |
| daily report no in progr | Feedback：日报只写已完成；死锁少写；未完进明日；推送仅 old-mac | `feedback_daily_report_no_in_progress.md` |
| daily report no padding | 日报禁硬凑（主人 2026-08-27） | `feedback_daily_report_no_padding.md` |
| daily report owner edit  | Feedback：日报按主人改定方向进化 | `feedback_daily_report_owner_edit_learn.md` |
| daily report push tg dm | Feedback：日报定稿后推送 TG 私聊（权威机 = AUTHORITY_HOST） | `feedback_daily_report_push_tg_dm.md` |
| data dictionary format | 数据字典就是简单的四栏表格（字段名、中文名、类型、说明），不要加额外内容 | `feedback_data_dictionary_format.md` |
| db dir is source code | 扫描表的 DDL/ETL 时必须把项目根 db/ 整个目录纳入源代码扫描范围，不只是 ops_system/。 | `feedback_db_dir_is_source_code.md` |
| ddl must sync verify etl | Before ALTER TABLE add/drop columns, first identify all ETL writers; … | `feedback_ddl_must_sync_verify_etl.md` |
| default to production co | 在本项目跑数据库查询时默认用 .claude/database/my.cnf（生产），除非用户显式说测试库。 | `feedback_default_to_production_config.md` |
| deprecate must offline d | 合表/废弃必须同批下线旧海豚 task | `feedback_deprecate_must_offline_dolphin_task.md` |
| dev session display name | Dev Session 显示名格式（主人钦定 2026-07-21） | `feedback_dev_session_display_name.md` |
| dev session no fake stag | 死规矩 · Dev Session 禁止空标 stage done（主人 2026-07-29） | `feedback_dev_session_no_fake_stage_done.md` |
| dolphin append task at e | 海豚挂任务：追加到列表最后 | `feedback_dolphin_append_task_at_end.md` |
| dual mac hub sync | Feedback：双 Mac · 旧机主控 + 记忆/任务双向同步 | `feedback_dual_mac_hub_sync.md` |
| dw user event detail lig | For dw.dw_user_event_detail checks, first reconcile by event_id count… | `feedback_dw_user_event_detail_lightweight_validation_first.md` |
| dw user event detail que | For this project, queries against dw.dw_user_event_detail must always… | `feedback_dw_user_event_detail_query_constraints.md` |
| dwd r ddl direct to scot | 缺 dwd_r / 要 fanout 写表时，表结构直接发给斯科特，禁止让狂人转 | `feedback_dwd_r_ddl_direct_to_scott.md` |
| dwd r new table eval | 新建 dwd_r 前必须评估量级/分桶；merge-engine 默认不保留第一条 | `feedback_dwd_r_new_table_eval.md` |
| ethan jobs filter | Ethan 岗位监控筛选规则（大数据/数仓开发 · 禁第三国远程与到岗） | `feedback_ethan_jobs_filter.md` |
| exclude landing page cli | dwd_landing_page_click 不是 dc-parent 项目的表，统计/核查时排除 | `feedback_exclude_landing_page_click.md` |
| file summary must use ma | 报告 / 总结里提到任何创建或修改过的文件路径都必须写成 markdown 链接（[name](relative/path)）方便点击，不… | `feedback_file_summary_must_use_markdown_links.md` |
| finish then commit push | 干完就提交并 push（主人 2026-10-30） | `feedback_finish_then_commit_push.md` |
| funnel datacheck samplin | Prefer sampling over large full-table reconciliations for the channel… | `feedback_funnel_datacheck_sampling.md` |
| group liveness bus ack n | 群聊探活 / bus 收条：勿再回 | `feedback_group_liveness_bus_ack_no_reply.md` |
| group reply only explici | 群聊回复：仅显式 @初儿 / @又初 | `feedback_group_reply_only_explicit_at.md` |
| investigate full story | 查问题要把来龙去脉查清楚 | `feedback_investigate_full_story.md` |
| landing page ip repeats  | landing_page_view/click IP 重复不应被当作 IP 异常，一个用户会多次触发；仍要报 NULL / CF-only… | `feedback_landing_page_ip_repeats_ok.md` |
| lineage origin is kafka | 任何血缘分析都必须把数据起点画到 Kafka 事件消息，dw 是统一具化层，dwd 是按事件类型的二次拆分，不能把 dwd 当源头。 | `feedback_lineage_origin_is_kafka.md` |
| memory light read | 记忆召回要轻（主人 2026-09-29） | `feedback_memory_light_read.md` |
| metric analysis doc temp | 每个需求分析/指标文档对标 metric_big_funnel_event_dictionary；写完 POST upload 提交平台文… | `feedback_metric_analysis_doc_template_and_upload.md` |
| new biz no shadow write  | 全新业务禁影子双跑；改 pb 目标须扫全清单，禁止只改两份 SQL | `feedback_new_biz_no_shadow_write_formal.md` |
| no bump extension versio | 死规矩 · 又初不改插件版本号 / 不自行发 vsix（2026-07-29 钦定 · 2026-08-04 再犯） | `feedback_no_bump_extension_version.md` |
| no workaround report wor | 共享组件出问题 · 直接反馈狂人，禁止私自绕过（2026-10-22） | `feedback_no_workaround_report_worker_ant.md` |
| omdb is portable no memo | omdb 子目录视作独立可分发项目；不要在 dc-parent 或 omdb 项目路径下保存任何 omdb 相关的 memory；约束写在… | `feedback_omdb_is_portable_no_memory.md` |
| ops system etl directory | ETL / Dev Session 统一放 data-jobs/dolphin 分层目录 | `feedback_ops_system_etl_directory_layout.md` |
| per app verification rul | 这条是**项目级根本规则**，覆盖设计 + ETL + 表结构 + bitmap hash + 指标核对 + 数据质量。不限于"核对场景"。 | `feedback_per_app_verification_rule.md` |
| pinned overflow append o | PINNED 1–30 冻结；新红线只追加 pinned/，禁止顶旧条 | `feedback_pinned_overflow_append_only.md` |
| prod bucket from prod pr | 产发 bucket/并行度只认 prod 探数，禁用 test 行数估配置 | `feedback_prod_bucket_from_prod_probe.md` |
| prod monitor follow work | 主人确认 prod 盯盘按狂人安排（告警驱动，不另建夜间全量扫） | `feedback_prod_monitor_follow_worker_ant.md` |
| prod release review gate | 要上 prod 时群里 @工作狂人 或 @知秋 交路径/方案/报告审核，由他们发布；又初只做 test 开发与验证。 | `feedback_prod_release_review_gate.md` |
| project is starrocks onl | dc-parent project is pure StarRocks; never write MySQL/PostgreSQL/Hiv… | `feedback_project_is_starrocks_only.md` |
| promotion video threshol | 项目通用定义：视频"有效播放" = play_duration >= 5（秒）。所有视频相关指标都按此口径过滤 video_play 事件。 | `feedback_promotion_video_threshold_gte5.md` |
| publish git local dolphi | 协作习惯 · 发布前三处代码必须一致 | `feedback_publish_git_local_dolphin_triple_sync.md` |
| quantify numeric error a | For every data validation, locate numeric discrepancy root cause; if … | `feedback_quantify_numeric_error_and_hll_tolerance.md` |
| reviewer usernames | 审核人平台账号（提审用） | `feedback_reviewer_usernames.md` |
| save relevant context pr | Proactively save durable user guidance and stable project context so … | `feedback_save_relevant_context_proactively.md` |
| self evolve on criticism | 遇到的问题与批评必须同会话沉淀成记忆，禁止只认错不落库 | `feedback_self_evolve_on_criticism.md` |
| spark OUT DB catalog onl | Spark · OUT_DB 只装 catalog（知秋 2026-09-24） | `feedback_spark_OUT_DB_catalog_only.md` |
| speak plain to user | 跟用户说话用通俗易懂的人话；少堆术语和清单腔 | `feedback_speak_plain_to_user.md` |
| sql datetime between edg | 字符串日期 'YYYY-MM-DD' 在和 DATETIME 列比较时被 cast 成 'YYYY-MM-DD 00:00:00'，BET… | `feedback_sql_datetime_between_edge_bug.md` |
| sql etl header three lin | Feedback：ETL SQL 文件头 + task.yaml（强制） | `feedback_sql_etl_header_three_lines.md` |
| starrocks default value  | StarRocks 不允许 ALTER 修改列默认值；DEFAULT CURRENT_TIMESTAMP 在主键表 UPDATE 时会踩坑 | `feedback_starrocks_default_value_caution.md` |
| starrocks primary key pa | In StarRocks primary key tables, partition columns must be included i… | `feedback_starrocks_primary_key_partition_rules.md` |
| task time estimation | Feedback：任务耗时预估 + 实际记录（持续校准） | `feedback_task_time_estimation.md` |
| test platform zsq18012 n | 测试平台连法（指标库）· 狂人 2026-11-26 | `feedback_test_platform_zsq18012_not_18013.md` |
| tg bus long message must | TG / agent-bus 长消息出站 | `feedback_tg_bus_long_message_must_split.md` |
| tg dm fast work dual tra | Feedback：TG 私聊长活占着时另开 agent（已落地） | `feedback_tg_dm_fast_work_dual_track.md` |
| tg no ask answer ok | TG SQL 答完禁止主动征询「这个回答合适吗？」与满意/不满意按钮 | `feedback_tg_no_ask_answer_ok.md` |
| upload cloud not tg | 用户说「上传云端」= 填报 HTML 对应 API，与 TG 无关 | `feedback_upload_cloud_not_tg.md` |
| user device base tables  | 写用户/设备维 SQL 前必读平台基础表使用说明 | `feedback_user_device_base_tables_usage_guide.md` |
| violations must show raw | 报告数据质量违规时必须给出表里能直接定位的真实行（event_id/PK/时间等），不能只给统计或意译描述。 | `feedback_violations_must_show_raw_rows.md` |
| vpn renew deadlock use c | VPN 续期死结 · 用变色龙打通外网（主人 2026-09-23） | `feedback_vpn_renew_deadlock_use_cham.md` |
| vpn renew every day | VPN 续期每天必跑（主人 2026-07-27 钦定） | `feedback_vpn_renew_every_day.md` |
| weekly report format loc | 仅周报：格式锁死、内容说人话；日报维持原写法 | `feedback_weekly_report_format_locked_plain_words.md` |
| weekly report style w28 | 周报以 W28 定稿为样板：按工作簿主责分专项、禁 bus#、只写数据工作 | `feedback_weekly_report_style_w28.md` |
| wide table structure fre | For wide-table metadata tasks, only use the user-provided current tab… | `feedback_wide_table_structure_freeze_and_input_source_preference.md` |
| work log multi agent rep | Feedback：work-log 跨 Agent + 双 Mac 共享（日报/周报） | `feedback_work_log_multi_agent_reports.md` |
| workbook mirror private | Feedback：工作簿镜像到私聊 | `feedback_workbook_mirror_private.md` |
| workbook progress confir | Feedback：工作簿进展 = 核对真实进度后自动发群 | `feedback_workbook_progress_confirm_before_group.md` |
| workbook progress cutoff | 工作簿进展：报「截至汇报前」而非「当天实活」 | `feedback_workbook_progress_cutoff_not_today.md` |
| workbook progress list p | Feedback：狂人 bus 任务清单问进度 → 清单主责 + 自开实责 · 统一查「截至汇报前」 | `feedback_workbook_progress_list_plus_owned_cutoff.md` |
| youchu gloss english ter | 对主人说话时，英文技术名词后紧跟中文翻译 | `feedback_youchu_gloss_english_terms_zh.md` |
| 主人说话风格复用 | 群聊、对狂人 bus、对主人回复，都要贴近主人口语风格：短、直接、先结论、少套话 | `feedback_主人说话风格复用.md` |
| 自开任务必须登工作簿 | 大活（逐条对齐需求那种）要登 workbook「自开任务」；吃不准就问主人 | `feedback_自开任务必须登工作簿.md` |
