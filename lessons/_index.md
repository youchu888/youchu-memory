# Lessons 索引

| 日期 | 标题 | tags | 一句话 |
|------|------|------|--------|
| 2026-08-09 | [工作簿拦截私聊刷屏：launchd 找不到 mysql + 拦截未去重](./2026-08-09-workbook-verify-block-dm-spam-mysql-path.md) | tgbot, workbook-progress, mysql, dm-spam | 拦截同一天只 DM 一次；MYSQL_BIN |
| 2026-08-09 | [ETL 跑通但 0 行时先核对 app_id 与源表行数，再决定是否换 app ](./2026-08-09-etl-跑通但-0-行时先核对-app_id-与源表行数-再决定是否换-app-补跑.md) | funnel-etl,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-09 | [宽漏斗禁单 SQL 宽聚合，拆成 metrics + wide 两阶段，避免 d](./2026-08-09-宽漏斗禁单-sql-宽聚合-拆成-metrics-wide-两阶段-避免-driver-heap.md) | funnel-etl,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-09 | [user_is_new 禁止 JOIN 无分区 dim_user_all，改由当](./2026-08-09-user_is_new-禁止-join-无分区-dim_user_all-改由当日-user_r.md) | funnel-etl,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-08 | [口径|is_new](./2026-08-08-口径-is_new.md) | spec,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-08 | [funnel|oom|etl](./2026-08-08-funnel-oom-etl.md) | spark,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [指定审核人发产须同时满足 publish_request_status=pend](./2026-08-07-指定审核人发产须同时满足-publish_request_status-pending-与-pu.md) | publish-prod,publish_request_status,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [并行处理私聊/工作簿时仍须 60 秒内 agent-bus ACK，核查完再 r](./2026-08-07-并行处理私聊-工作簿时仍须-60-秒内-agent-bus-ack-核查完再-reply-禁止漏.md) | agent-bus,ack,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [群工作簿进度发群前必须 prod 实查分区/验数，禁止只看 test 或 dev](./2026-08-07-群工作簿进度发群前必须-prod-实查分区-验数-禁止只看-test-或-dev-session.md) | workbook-progress,prod-check,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [群工作簿进展须当日实查整理，新大活次日登簿汇报](./2026-08-07-群工作簿进展须当日实查-新大活次日登簿.md) | workbook-progress, tgbot, supplemental, criticism | 禁止复读硬编码；大漏斗登 supplemental#11 |
| 2026-08-07 | [报补数窗口与耗时时查全部分区 etl_time 与海豚实例，并区分「发起窗口」与](./2026-08-07-报补数窗口与耗时时查全部分区-etl_time-与海豚实例-并区分-发起窗口-与-表实际最早可落.md) | complement,datacheck,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [日报正文只用业务说法（如「五月至今补刷」），禁止写入内部分区区间、耗时秒数、PI](./2026-08-07-日报正文只用业务说法-如-五月至今补刷-禁止写入内部分区区间-耗时秒数-pi-等核对细节.md) | daily-report,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-07 | [写日报前必须先 prod/test/平台逐项核查再落稿，状态与补数范围禁止凭印象](./2026-08-07-写日报前必须先-prod-test-平台逐项核查再落稿-状态与补数范围禁止凭印象或局部样本.md) | daily-report,datacheck,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-06 | [bus 转发须自检正文完整；截断导致对方看不到问题时立即补发全量说明再结案](./2026-08-06-bus-转发须自检正文完整-截断导致对方看不到问题时立即补发全量说明再结案.md) | agent-bus,messaging,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-06 | [问指标是否被改时先查平台 metric 文档并对本地 diff，同时读齐私聊上文](./2026-08-06-问指标是否被改时先查平台-metric-文档并对本地-diff-同时读齐私聊上文-禁止跨轮次漏读.md) | context-continuity,platform-docs,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-06 | [狂人未更新工作簿时，自开任务写 workbook_supplemental.js](./2026-08-06-狂人未更新工作簿时-自开任务写-workbook_supplemental-json-合并逻辑按.md) | workbook,task-tracking,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-05 | [主人说「stage1-6 干完先不发」时：可标 stage done + tes](./2026-08-05-主人说-stage1-6-干完先不发-时-可标-stage-done-test-跑通-但-禁止-.md) | dev-session-stage,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-05 | [进入=会话首页且来路非空；刷新不算跳转；空 uid/device 丢弃——改 E](./2026-08-05-进入-会话首页且来路非空-刷新不算跳转-空-uid-device-丢弃-改-etl-前先核对这三.md) | page-visit-caliber,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-05 | [一个 PRD「页面访问」按指标类型拆成 visit_d（日指标）与 jump_d](./2026-08-05-一个-prd-页面访问-按指标类型拆成-visit_d-日指标-与-jump_d-跳转分布-两个.md) | page-visit,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-04 | [日报对照主人改定稿学习写法](./2026-08-04-日报对照主人改定学习.md) | daily-report, learning | 结果向少旁白；明日动作可多条估截止 |
| 2026-08-04 | [extension|security|官方 vsix 安装前必须 SHA256 ](./2026-08-04-extension-security-官方-vsix-安装前必须-sha256-校验通过-禁止跳.md) | dc-platform,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-04 | [extension|dual-mac|双机无 SSH 时扩展升级须各机本地跑 s](./2026-08-04-extension-dual-mac-双机无-ssh-时扩展升级须各机本地跑-sync-memo.md) | dc-platform,session-rotate | 会话轮换前自动蒸馏 |
| 2026-08-04 | [日报只写已完成；死锁少写；推送仅 old-mac](./2026-08-04-daily-report-no-in-progress.md) | daily-report, dual-mac, tg | 已完成→结果；未完→明日；死锁空；old-mac 推私聊 |
| 2026-08-04 | [日报定稿后必须推送 TG 私聊](./2026-08-04-daily-report-push-tg-dm.md) | tg, daily-report, dm | 仅 old-mac 跑 memory/scripts/post_daily_report_to_dm.py |
| 2026-08-03 | [归因 Paimon 影子全链 test](./2026-08-03-attribution-paimon-shadow-full-chain-test.md) | attribution-shadow, paimon, dolphin | 独立 wf+_r 全链；test 湖空则 0 行；真压测等湖或 prod |
| 2026-08-03 | [提交只动 ops_system：禁改平台插件与 api_v1](./2026-08-03-禁改平台插件与api_v1.md) | git, ownership, 禁改 | vscode-extension/dc-platform-server 禁改；误 push 则新 commit 恢复 |
| 2026-08-01 | [prod 补数全员开放](./2026-08-01-prod-complement-open-all-users.md) | dolphin, complement, prod | env=prod 补数非admin可用；三坑 dep_type/日期/force |
| 2026-08-01 | [butler 原生图记忆体系](./2026-08-01-butler-native-memory-system.md) | memory, butler, self-evolve | 项目.claude/memory+sqlite；六工具；写前query；读timeline+query |
| 2026-08-01 | [做事要考虑健壮性](./2026-08-01-robustness-first.md) | robustness, habit, ops | 失败自愈、不滚雪球、脚本同源、改完 smoke |
| 2026-08-01 | [新 Mac memory 同步总失败因旧脚本](./2026-08-01-new-mac-memory-sync-old-script.md) | memory-git, dual-mac, new-mac, launchd | LaunchAgent 跑 07-24 旧脚本无自愈；应对齐 memory/scripts 新版 |
| 2026-07-31 | [Dev Session 1–6 必须逐步做完否则别人打不开](./2026-07-31-dev-session-stages-complete-or-others-cant-open.md) | dev-session, stage1-6, publish_runs, strict | 禁空标 done/半截收工；产物+证据+push 齐再收口 |
| 2026-07-31 | [提交后立刻推远程禁止分两步](./2026-07-31-commit-then-push-no-two-steps.md) | git, push, feedback | 入库/commit 成功即 push；勿再问要不要推 |
| 2026-07-31 | [提交说明用第一人称直述禁我/主人/旁白](./2026-07-31-first-person-commit-voice.md) | git, commit, voice | 直述做了什么；禁「我/主人/旁白体」 |
| 2026-07-31 | [Stage4 海豚段不可半截](./2026-07-31-stage4-finish-dolphin-not-skip.md) | stage4, dolphin_test | 三勾后必须补数对账再标 done |
| 2026-07-28 | [回懂了必须立刻开干](./2026-07-28-ack-must-start-work.md) | ack, execution, criticism | ACK 后同会话动手，禁口头确认后静默 |
| 2026-07-28 | [群聊仅显式 @初儿/@又初 才回，取消裸喊名](./2026-07-28-群聊仅显式at初儿又初才回.md) | tg, group, mention, silent | 废止裸喊名；@worker_ant+文案带又初不再秒回 |
| 2026-07-28 | [探活 / bus 收条类对话：已闭环则勿再回](./2026-07-28-探活与bus收条无需再回.md) | tg, group, silent, liveness, bus-ack | 还活着吗/bus收到了吗/收到这块我跟 → 不回；禁 Cursor 叠回 |
| 2026-07-28 | [vsix 放 dc-platform-server/extension/ 走 g](./2026-07-28-vsix-放-dc-platform-server-extension-走-git-pull-s.md) | extension,release,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-28 | [device_id 空率≥90%（本需求 100%）则直建 dim_device](./2026-07-28-device_id-空率-90-本需求-100-则直建-dim_device_all-勿再设计-.md) | device_tag,dim,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-28 | [PRD 五档看板只查 session_duration 合表并带 stat_gr](./2026-07-28-prd-五档看板只查-session_duration-合表并带-stat_grain-page.md) | session_duration,backend,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-27 | [bus-reply|bus 派活要求「结论请回 bus」时，验完直接 agent](./2026-07-27-bus-reply-bus-派活要求-结论请回-bus-时-验完直接-agent-bus-结案-.md) | tg-group,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-27 | [群聊双 @ strip 误判没@初儿](./2026-07-27-group-dual-at-strip-false-negative.md) | tgbot,group,mention | strip @youchu 后 Agent 只见 mudan → 误回不回；已修 |
| 2026-07-27 | [mention-routing|未 @youchu_ai_bot 的群消息直接不](./2026-07-27-mention-routing-未-youchu_ai_bot-的群消息直接不回-且不在群里解释.md) | tg-group,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-27 | [bot 自查告警：连续失败才私聊](./2026-07-27-bot-selfcheck-notify-after-sustained.md) | tgbot, watchdog, alert | NOTIFY_AFTER=3；getMe 后跳过二次探活 |
| 2026-07-27 | [VPN 续期不因请假/节假日停止](./2026-07-27-vpn-renew-never-skip-leave-holiday.md) | vpn, leave, holiday, launchd | 每天必续；请假日历不管 VPN |
| 2026-07-25 | [bus 入站（含 mudan99 等 peer）与 TG @ 同优先级当天回；私](./2026-07-25-bus-入站-含-mudan99-等-peer-与-tg-同优先级当天回-私聊极简时群里仍要主动.md) | agent-bus,collab,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [发布顺序固定为本地→git push→海豚，发布后 live SQL 与 git](./2026-07-25-发布顺序固定为本地-git-push-海豚-发布后-live-sql-与-git-sha-dif.md) | publish,dolphin,git,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [开通归因前先查配置表有无行；无行 INSERT、有行再 UPDATE；增量开通勿](./2026-07-25-开通归因前先查配置表有无行-无行-insert-有行再-update-增量开通勿跑-bulk-i.md) | attribution,prod-config,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [发布前三处代码必须一致 git/本地/海豚](./2026-07-25-publish-git-local-dolphin-triple-sync.md) | dolphin,git,publish,session-rotate | 发布完成=三处同 SHA；先 push 再发海豚；发布后 diff live SQL |
| 2026-07-25 | [开通归因=配置表 is_run=1 + 客户端 attribution_flag](./2026-07-25-开通归因-配置表-is_run-1-客户端-attribution_flag-1-双开-诊断报告.md) | attribution,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [提审 @ 审核人用 `@mudan99_bot`（野花），禁止 @ 主人代审](./2026-07-25-提审-审核人用-mudan99_bot-野花-禁止-主人代审.md) | collaboration,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [本地合表/改 outputs 后立刻用平台 API 同步 session，勿假设](./2026-07-25-本地合表-改-outputs-后立刻用平台-api-同步-session-勿假设插件已跟上.md) | dev-session,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [星型模型设计 playbook 已沉淀](./2026-07-25-star-schema-design-playbook.md) | star-schema,design,dws,ads,playbook | 设计 DWS/ADS 前读 playbooks/star_schema_design.md；六原则+checklist |
| 2026-07-25 | [page_stay 是 uid×dt 事实表，session_duration ](./2026-07-25-page_stay-是-uid-dt-事实表-session_duration-是多维预聚合-合.md) | duration_model,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [test 上 dws 删表/改 PK 用 root@43.212.113.132](./2026-07-25-test-上-dws-删表-改-pk-用-root-43-212-113-132-9030-勿用.md) | test_db,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [五档 DWS 合表用 stat_grain 区分单次/日均，查询必带该列，否则两](./2026-07-25-五档-dws-合表用-stat_grain-区分单次-日均-查询必带该列-否则两种-y-轴会混算.md) | session_duration,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [归因 shadow 读 Paimon register + landing cl](./2026-07-25-归因-shadow-读-paimon-register-landing-click-view-开.md) | attribution-shadow,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [群聊进度第一句给结论，回前核对 bus 实态，列点 ≤4 条用 `·`，验完 b](./2026-07-25-群聊进度第一句给结论-回前核对-bus-实态-列点-4-条用-验完-bus-结案再群里一句带过.md) | tg-group,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-25 | [影子压测用独立 Spark wf + `_shadow` 表，源侧对齐后再首跑，](./2026-07-25-影子压测用独立-spark-wf-_shadow-表-源侧对齐后再首跑-严禁动现网-sr.md) | paimon-shadow,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [群聊问进度禁止秒回「行，我来」罐头 ACK](./2026-07-24-progress-ask-no-instant-ack.md) | tg, group, progress, instant-ack, self-evolve | 进度问 → direct 短报；禁 instant ack |
| 2026-07-24 | [跨 Agent 分工对齐走 bus 互督 checkpoint，不在群里公开回复](./2026-07-24-跨-agent-分工对齐走-bus-互督-checkpoint-不在群里公开回复派活细节.md) | agent-bus,tg,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [归因 apply 须同步回写 `dim_user_daily_snapshot`](./2026-07-24-归因-apply-须同步回写-dim_user_daily_snapshot-t-1-分区-ch.md) | attribution,dim,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [查岗 handler 未命中须打 debug 日志，触发条件收成「抽查群 @ 即](./2026-07-24-查岗-handler-未命中须打-debug-日志-触发条件收成-抽查群-即尝试解析-勿依赖固定.md) | attendance,tgbot,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [日报上传云端须主人显式指令；只传 `reports/日报-YYYY-MM-DD.](./2026-07-24-日报上传云端须主人显式指令-只传-reports-日报-yyyy-mm-dd-md-定稿全文-禁.md) | daily-report,upload,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [停 18:00 页面停留推狂人须卸载 `com.youchu.page-stay](./2026-07-24-停-18-00-页面停留推狂人须卸载-com-youchu-page-stay-18h-laun.md) | page-stay,launchd,agent-bus,session-rotate | 会话轮换前自动蒸馏 |
| 2026-07-24 | [TG 群发 urllib 超时则 kill 进程并改用 curl 重发，成功后再](./2026-07-24-tg-群发-urllib-超时则-kill-进程并改用-curl-重发-成功后再报-已到达.md) | tg-send,urllib,curl,session-rotate | 会话轮换前自动蒸馏 |
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
| 2026-07-27 | [merge_pool 多桶 OVERWRITE](./2026-07-27-merge-pool-stage4-overwrite-and-publish.md) | merge_pool, stage4 | 同分区串行桶会互覆盖；默认 bucket_n=1 |
| 2026-07-28 | deprecate-must-offline-old-dolphin-task | high | dolphin,deprecate,half-migration | 合表废弃必须同批删旧海豚 task，禁半迁移 |
| 2026-08-03 | [查岗未回：work_online 克隆 session 双连抢更新](./2026-08-03-查岗未回因work_online克隆session双连抢更新.md) | attendance,tgbot,telethon | 同 auth_key 双连导致 NewMessage 丢失 |
| 2026-08-04 | [新 Mac 出站不同步：回旧机勿改链路](./2026-08-04-new-mac-outbound-tg-direct.md) | agent-bus,tg,new-mac,dual-mac | bot 活归旧机；新机勿加直推 |
