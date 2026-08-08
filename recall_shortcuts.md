# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 08 2026 agent_session_rotate cursor d | `~/.dc-platform/memory/lessons/2026-08-08-口径-is_new.md` | 2026-08-08-口径-is_new |
| ## 08 2026 agent_session_rotate cursor d | `~/.dc-platform/memory/lessons/2026-08-08-funnel-oom-etl.md` | 2026-08-08-funnel-oom-etl |
| etl oom paimon session 「能 「降 | `sessions/tg-rotate-2026-08-08-2153.md` | 大漏斗链路推进状态：平台 session 已建，Paimon 建表、日批 ETL |
| tg top1 「今 「明 「明日动作」只保留 」不 | `sessions/tg-rotate-2026-08-08-2153.md` | 日报格式偏好：主人要求「今日结果」不写第二条、「明日动作」只保留 TOP1；改定 |
| playbook.md 与知 于与 便于 便于与知秋对齐复验 关键 | `sessions/tg-rotate-2026-08-08-2153.md` | 冒烟验收应覆盖：耗时、输出行数、关键指标抽样；可沉淀到 `playbook.md |
| 03 04.dws 08 2026 81 app_2556 | `sessions/tg-rotate-2026-08-08-2153.md` | 下一轮验收建议跑第 4 轮 SF-81 冒烟（S 档），示例命令：`bash o |
| diff sql 做本 先做 入集 再进 | `sessions/tg-rotate-2026-08-08-2153.md` | 改完 SQL 后先做本地 diff 自检，确认改动范围只在大漏斗目录、无旁路误改 |
| dim_user_daily_snapshot is_new spark spe | `sessions/tg-rotate-2026-08-08-2153.md` | 当前 Spark 版 `is_new` 临时口径：以当日 `user_regis |
| keys oom 「一 「按 」拆 一条 | `sessions/tg-rotate-2026-08-08-2153.md` | 抗 OOM 改法：把「一条大聚合」拆成「按事件独立聚合 + 以 keys 外连接 |
| 04.dws design.md dws_app_event_funnel_d_ | `sessions/tg-rotate-2026-08-08-2153.md` | 大漏斗任务工作目录固定为 `ops_system/04.dws/dws_app_ |
| dim_user_daily_snapshot is_new lesson sp | `sessions/tg-rotate-2026-08-08-2153.md` | [LESSON: spec/口径/is_new] 临时口径与目标口径并存时，必须 |
| design.md etl memory.m memory.md spec.md | `sessions/tg-rotate-2026-08-08-2153.md` | 重构 ETL 时必须同步三处文档：`spec.md`（口径）、`design.m |
| case... count distinct oom stage stage37 | `sessions/tg-rotate-2026-08-08-2153.md` | stage37 OOM 根因是单条超宽 `COUNT(DISTINCT CASE |
| ## 07 08 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-07-指定审核人发产须同时满足-publish_request_status-pending-与-pu.md` | 2026-08-07-指定审核人发产须同时满足-publish_request_ |
| ## 07 08 2026 60 ack | `~/.dc-platform/memory/lessons/2026-08-07-并行处理私聊-工作簿时仍须-60-秒内-agent-bus-ack-核查完再-reply-禁止漏.md` | 2026-08-07-并行处理私聊-工作簿时仍须-60-秒内-agent-bus |
| ## 07 08 2026 agent_session_rotate check | `~/.dc-platform/memory/lessons/2026-08-07-群工作簿进度发群前必须-prod-实查分区-验数-禁止只看-test-或-dev-session.md` | 2026-08-07-群工作簿进度发群前必须-prod-实查分区-验数-禁止只看 |
| prepare_daily_report_sync.sh 上传 不写 云端 产跟 | `sessions/tg-rotate-2026-08-07-2244.md` | 日报：先跑 `prepare_daily_report_sync.sh` 双机同 |
| 001 20260728 dev false i_can_publish_pro | `sessions/tg-rotate-2026-08-07-2244.md` | 订单发产（`dev-20260728-ura-001`）：test 就绪 ≠ 可 |
| #6 06 10 60 61 ack | `sessions/tg-rotate-2026-08-07-2244.md` | agent-bus 与私聊并行：处理 A 时不能漏 B；**60 秒内 ACK* |
| prod pv test uv 不能 不能逐行对 | `sessions/tg-rotate-2026-08-07-2244.md` | prod/test 对账：test 为稀疏采样，**不能逐行对 prod**；回 |
| #1 002 05 0） 10 20260 | `sessions/tg-rotate-2026-08-07-2244.md` | 页面访问（#10）：prod `dws_app_page_visit_d_d`  |
| #9 06 08 31 9） dws_session_duration_user | `sessions/tg-rotate-2026-08-07-2244.md` | 停留时长（#9）：prod `dws_session_duration_user |
| dev log pending pending） prod rp | `sessions/tg-rotate-2026-08-07-2244.md` | 群工作簿进度以 **prod 实查** 为准：prod 有近期分区即标「已完成」 |
| 60 ack agent bus lesson reply | `sessions/tg-rotate-2026-08-07-2244.md` | [LESSON: agent-bus,ack/并行处理私聊/工作簿时仍须 60  |
| check dev lesson pending prod progress | `sessions/tg-rotate-2026-08-07-2244.md` | [LESSON: workbook-progress,prod-check/群工 |
| none pass status test 「申 不以 | `sessions/tg-rotate-2026-08-07-2244.md` | 发产卡在 `status=none`：让申请人（蓝猫）重提「申请发布」；审核人发 |
| prod session 不能凭 主人 主人已多次强调 人已 | `sessions/tg-rotate-2026-08-07-2244.md` | 每日群进度须 **发群前 prod 验数门禁**；主人已多次强调，不能凭 ses |
| bash omdb pending prod restart.sh ses | `sessions/tg-rotate-2026-08-07-2244.md` | `workbook_progress_service.py` 旧逻辑三坑：只查  |
| ## 07 08 2026 agent_session_rotate compl | `~/.dc-platform/memory/lessons/2026-08-07-报补数窗口与耗时时查全部分区-etl_time-与海豚实例-并区分-发起窗口-与-表实际最早可落.md` | 2026-08-07-报补数窗口与耗时时查全部分区-etl_time-与海豚实例 |
| ## 07 08 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-07-日报正文只用业务说法-如-五月至今补刷-禁止写入内部分区区间-耗时秒数-pi-等核对细节.md` | 2026-08-07-日报正文只用业务说法-如-五月至今补刷-禁止写入内部分区区 |
| ## 07 08 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-07-写日报前必须先-prod-test-平台逐项核查再落稿-状态与补数范围禁止凭印象或局部样本.md` | 2026-08-07-写日报前必须先-prod-test-平台逐项核查再落稿-状 |
| force mac old tg 不反 不反复污染对外稿 | `sessions/tg-rotate-2026-08-07-0604.md` | 更正日报后可在 old-mac 上 force 重推 TG 私聊；核查过程与修正 |
| 与用 事件 于已 件统 任务 优先 | `sessions/tg-rotate-2026-08-07-0604.md` | 【明日动作】须对齐当前任务盘，而非随手写跟进项：大漏斗事件统计表 + 指标文档、 |
| de dev pending rp session 「审 | `sessions/tg-rotate-2026-08-07-0604.md` | 平台/session 状态须真查再写：页面访问 RP 在野花侧 **pendin |
| 01 01～08 05 07 36 「0 | `sessions/tg-rotate-2026-08-07-0604.md` | 补数窗口说「五月至今」时，若表/上游七月才有分区，内部心知实际落库范围，但**对 |
| 31 is_valid ≠「 「口 「口径补丁 「首 | `sessions/tg-rotate-2026-08-07-0604.md` | 「口径补丁/补刷」≠「首次生产发布」：停留时长 7/31 已上线，当日仅是 `i |
| 21 30 prepare_daily_report_sync.sh tg 主人 | `sessions/tg-rotate-2026-08-07-0604.md` | 21:30 定时任务漏推日报时，主人提醒后须先跑双机同步（`prepare_da |
| daily lesson pi# report 「五 」） | `sessions/tg-rotate-2026-08-07-0604.md` | [LESSON: daily-report/日报正文只用业务说法（如「五月至今补 |
| daily datacheck lesson prod report test | `sessions/tg-rotate-2026-08-07-0604.md` | [LESSON: daily-report,datacheck/写日报前必须先  |
| 上传 上传云端须 不动 主人 云端 人定 | `sessions/tg-rotate-2026-08-07-0604.md` | 日报被主人定稿后，上传云端须**原封不动**用给定正文，禁止改写后再传。 |
