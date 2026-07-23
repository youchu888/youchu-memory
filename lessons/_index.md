# Lessons 索引

| 日期 | 标题 | tags | 一句话 |
|------|------|------|--------|
| 2026-07-23 | [get_task_instance_log 约 64KB 截断拿不到 SR 尾部](./2026-07-23-get_task_instance_log-约-64kb-截断拿不到-sr-尾部错-需海豚-ui.md) | dolphin,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-23 | [单 task 秒级 FAIL 且补跑成功：先跑验恢复四件套再判瞬时资源问题，不必](./2026-07-23-单-task-秒级-fail-且补跑成功-先跑验恢复四件套再判瞬时资源问题-不必改-sql.md) | dolphin,datacheck,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-23 | [prod 集群 SSH 用 ec2-user@175.41.188.204，勿用](./2026-07-23-prod-集群-ssh-用-ec2-user-175-41-188-204-勿用-hadoop-.md) | dolphin,ssh,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-23 | [会话轮换必须先沉淀再清空](./2026-07-23-session-rotate-must-distill-first.md) | tg,session-rotate,self-evolve,feedback | 清 resume 前必蒸馏；carry+lesson+通知 |
| 2026-07-21 | [Dev Session 对外汉字名 · 禁 code/项目id](./2026-07-21-dev-session-display-name-format.md) | dev-session, naming, feedback, tg, project | 发群/新建用【标签】表名 · 又初；禁 dev-xxx 与海豚 project_code 对外 |
| 2026-07-22 | [双 Mac work-log 统一后再写日报](./2026-07-22-dual-mac-worklog-unified-daily-report.md) | daily-report, work-log, dual-mac, sync | hosts 分流+合并；sync-memory-git 自动导出；正式稿进 memory/work-log/reports |
| 2026-07-15 | [日报周报语气：通俗但正式](./2026-07-15-report-plain-but-formal-style.md) | daily-report, weekly-report, writing-style, communication | 主人钦定；非技术看懂+书面语气；术语翻业务话、禁口语俚语；playbook+daily-report.mdc 已同步 |
| 2026-07-15 | [停留时长进度+群知秋钦定要点](./2026-07-15-stay-duration-and-group-directives.md) | stay-duration, session, dws_session_duration, attribution, tag, zhiqiu, group | Phase1(page_stay/sid)test闭环待prod提审；Phase2知秋令转DWS会话时长(账户+设备)墙钟五档待拍；宏/人工节点/分层铁律 |
| 2026-07-13 | [工作簿负责人以最新一日为准](./2026-07-13-workbook-ownership-latest.md) | workbook, ownership, group, feedback | 禁沿用过期归属；07-12 起停留时长改派又初 |
| 2026-07-09 | [VPN 续期按导入时刻滚动](./2026-07-09-vpn-renew-by-import-time.md) | vpn, launchd, ops | imported_at 记上次导入；满 23h 提前续；非固定零点 |
| 2026-07-08 | [日报禁止写 bus 编号须写任务名](./2026-07-08-daily-report-no-bus-id.md) | daily-report, feedback, bus | 主人钦定；日报正文禁 bus#；写任务名；已改正 daily-report.mdc |
| 2026-07-08 | [日报须汇总多 Agent 流水](./2026-07-08-daily-report-multi-agent-worklog.md) | daily-report, work-log, multi-agent | 先读 work-log 当日文件+全 transcript，勿只写当前会话 |
| 2026-07-08 | [归因出数硬条件与测试验收手册](./2026-07-08-attribution-test-gates-handbook.md) | attribution, test, gate, handbook | 入围/成功/回写门槛；HTML 手册路径 Downloads |
| 2026-07-08 | [内容排行猫猫线按令撤回](./2026-07-08-content-rank-handoff-rollback.md) | content-ranking, division, worker_ant | 代管撤回即停；勿冒领已完成 |
| 2026-07-07 | [监控群聊上下文定时归档](./2026-07-07-group-chat-context-archive.md) | tg, group, context, memory, archive | context.jsonl 瘦身→group_chat/archive；_search.jsonl 检索；bot 心跳每小时触发 |
| 2026-07-01 | [rewrite_status DDL 未同步 ETL 28≠27 活教材](./2026-07-01-rewrite-status-prod-ddl-etl-mismatch.md) | attribution, ddl, prod, rewrite_status, worker_ant | bus#617 知秋钦定；半上线→0秒FAIL→22表连锁；DDL+ETL同批+显式列清单 |
| 2026-07-02 | [群聊权威点名秒回 知秋/狂人](./2026-07-02-group-roll-call-authority-reply.md) | tg, group, roll-call, worker_ant | 在吗/谁活着/机器人挂了→健康则秒回；group_roll_call_handler |
| 2026-07-02 | [agent-bus 静默吞单两坑 seal+needs_reply](./2026-07-02-agent-bus-静默吞单两坑.md) | agent-bus, poller, worker_ant, feedback | bus#944 seal 误封；bus#980 漏判；狂人直派默认需 reply |
| 2026-07-02 | [bus 派活先回能接吗](./2026-07-02-bus-dispatch-先回能接吗.md) | agent-bus, worker_ant, 协作习惯 | 正文含先回能接吗→首条 reply 先答能接否+并行冲突 |
| 2026-07-02 | [agent-bus TG 镜像三坑 + 反套娃纪律](./2026-07-02-agent-bus-tg-mirror-anti-nesting.md) | agent-bus, tg, feedback, prod | no-dedup 必 mirror；未 unblock 勿 done；改 bot 前验 sendMessage |
| 2026-07-02 | [wf 权威名 wf_dws_汇总_日 · prod UI legacy dws_日](./2026-07-02-dolphin-prod-test-wf-name-map.md) | dolphin, prod, attribution, wf-map | canonical=wf_dws_汇总_日；prod API 用 code，UI 仍显示 dws_日 |
| 2026-07-01 | [bus 增补：干完也要 reply](../lessons/2026-07-01-agent-bus-reply-even-if-done.md) | agent-bus, worker_ant, feedback | 旧铁律不变；已做完仍 ACK+reply，附证据 |
| 2026-07-01 | [agent-bus「等待执行」误报](../lessons/2026-07-01-agent-bus-progress-ide-heartbeat.md) | agent-bus, progress, cursor | IDE 主会话干活但 progress 只盯 CLI；reply:bus 键结案 |
| 2026-07-01 | [归因 test DAG 与发布判断](../lessons/2026-07-01-attribution-test-dag-publish-gate.md) | attribution, dolphin, prod, publish | test 线上=repo 则无需再发；prod 群请示知秋 |
| 2026-07-01 | [归因 E2E 文档 + SF-81 灰度对数](./2026-07-01-attribution-e2e-platform-doc-and-sf81-gray.md) | attribution, gray, SF-81, test, platform-doc | 平台 doc 沉淀；test dim 同步后 TASK_ONLY apply 516/516 通过 |
| 2026-06-29 | [海豚 SQL 块注释 INSERT 0 行](./2026-06-29-dolphin-sql-block-comment-zero-rows.md) | dolphin, sql, attribution, prod | INSERT 前禁 `/* */` 块注释；用 `--`；SUCCESS 仍须查行数 |
| 2026-06-27 | [依工作狂人持续进化](./20260627-youchu-evolve-from-worker-ant.md) | worker_ant, self-evolve | 派单收尾提炼；纠正入库；禁止重复ack |
| 2026-06-27 | [agent-bus offset 四步修法](./20260627-agent-bus-offset-persistence.md) | agent-bus, poller, feedback | after_id 落盘/逐条推进/首轮跳 backlog/去重 |
| 2026-06-27 | [记忆体系与自我进化](./20260627-worker-ant-memory-architecture.md) | memory, feedback, worker_ant | 三级分层/触发词/Why+How/去重铁律 |
| 2026-06-27 | [工作狂人全量协作核心包](./20260627-worker-ant-full-collab-core.md) | worker_ant, etl, migration, dolphin | bus#77 七章；dynamic_overwrite/cat/海豚API/踩坑 |
| 2026-06-26 | [工作狂人协作速查 v1](./20260626-worker-ant-collab-cheatsheet.md) | worker_ant, starrocks, datacheck, prod | 速查简版；agent-bus bus#72 |
| 2026-06-24 | [ETL 统一 ops_system 分层目录](./2026-06-24-ops-system-etl-directory-layout.md) | ops_system, etl, dev-session, chcode | 禁仓库根 dwd_/dws_ session；SQL+文档同目录进 ops_system 对应层 |
| 2026-06-18 | [work-log 跨 Agent 共享](feedback_work_log_multi_agent_reports.md) | work-log, agent, daily-report | 本地 work-log/ 日流水；子 Agent 收尾必 append；不进 Git |
| 2026-06-18 | [ETL SQL 文件头三行声明](./2026-06-18-sql-etl-header-three-lines.md) | sql, lint, dolphin, etl | 前 30 行须 task/doc/params + 同目录 task.yaml；注释禁占位符 |
| 2026-06-17 | [StarRocks ALTER DEFAULT + PK MODIFY](./2026-06-17-starrocks-alter-default-and-pk-modify.md) | starrocks, ddl, primary-key | ADD DEFAULT 0 报错；主键表 key 列禁止 MODIFY |
| 2026-06-17 | [dc-platform 项目化记忆统一](./2026-06-17-dc-platform-projectization.md) | dc-platform, memory, archive | 公共记忆迁 ~/.dc-platform/memory/；task.yaml project=dc-platform |
| 2026-06-13 | [海豚发布 schedule 仍 OFFLINE](./2026-06-13-dolphin-publish-schedule-offline.md) | dolphin, schedule, dependent, video, test | wf PUT 后须 online_schedule；globalParams 与 repo SQL 须与线上一致 |
| 2026-06-10 | [核查规则沉淀剧本](./20260610-datacheck-playbook-as-asset.md) | datacheck, playbook, attribution, process | 核查认可后必更新 playbooks/；lesson 记坑、剧本记可执行 SQL |
| 2026-06-09 | [attribution_flag 列错位](./20260609-attribution-flag-column-order.md) | attribution, dwd, dolphin, test, schema | ALTER 追加列后须 INSERT 显式列名；小时任务缺字段会把 etl_time 写进 attribution_flag |
| 2026-06-05 | [归因 test 发布补数零行核验](./20260605-attribution-test-deploy-backfill.md) | attribution, dolphin, test, complement, dim | dim 须大写 app_id；补数 SUCCESS+0 行先查注册与落地页 IP 交集 |
| 2026-06-03 | [归因分析按 app 独立](./20260603-attribution-analyze-by-app.md) | attribution, datacheck, prod, per-app | 注册归因必须分 app 看漏斗与匹配因子；混算掩盖无候选/阈值差异 |
| 2026-06-03 | [生产 LTV 补数 readonly 限制](./20260603-prod-ltv-backfill-readonly.md) | prod, ltv, dolphin, complement, readonly | 生产 SR readonly + 无 prod 海豚写权限 → 必须海豚 UI/ETL 账号补数，不能直接 INSERT |
| 2026-05-29 | [dad-dau 分层根因与逐层核查](./2026-05-29-dad-dau-layered-root-cause.md) | datacheck, ads, dwd, dw, device_id, dad, dau | TJ-001 DAD 900w 根因在客户端 device_id 高 churn + ADS 口径含匿名 device；datacheck 必须逐层追到 dw |
