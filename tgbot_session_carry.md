# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-08 · 最新归档：`sessions/tg-rotate-2026-08-08-2153.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- stage37 OOM 根因是单条超宽 `COUNT(DISTINCT CASE...)` 同时在单个 stage 维护过多 distinct 集合，内存峰值过高。
- 重构 ETL 时必须同步三处文档：`spec.md`（口径）、`design.md`（数据流/实现）、`memory.md`（进展与待验项），避免代码与口径脱节。
- [LESSON: spec|口径|is_new] 临时口径与目标口径并存时，必须在 spec 写明当前实现来源与未接入的上游（如 `dim_user_daily_snapshot`），避免验数按错标准。
- 大漏斗任务工作目录固定为 `ops_system/04.dws/dws_app_event_funnel_d_d/`；续做前先读 `spec.md` / `design.md` / `memory.md` / `task` 定位卡点，再动 SQL。
- 抗 OOM 改法：把「一条大聚合」拆成「按事件独立聚合 + 以 keys 外连接拼宽表」；先保口径不变，再验可跑性。
- 当前 Spark 版 `is_new` 临时口径：以当日 `user_register` 事件推导，不用 `uid=-1`；目标来源是 `dim_user_daily_snapshot`，但现阶段不直连，需在 spec 里显式标注。
- 改完 SQL 后先做本地 diff 自检，确认改动范围只在大漏斗目录、无旁路误改，再进入集群冒烟。
- 下一轮验收建议跑第 4 轮 SF-81 冒烟（S 档），示例命令：`bash ops_system/04.dws/dws_app_event_funnel_d_d/spark/scripts/run_yarn_daily_sql.sh 2026-08-03 S app_2556`。
- 冒烟验收应覆盖：耗时、输出行数、关键指标抽样；可沉淀到 `playbook.md` 便于与知秋对齐复验。
- 日报格式偏好：主人要求「今日结果」不写第二条、「明日动作」只保留 TOP1；改定稿后需重新推 TG 私聊。
- 大漏斗链路推进状态：平台 session 已建，Paimon 建表、日批 ETL、设计说明与核查剧本已落库；当前重点从「能跑通」转向「降 OOM 风险后复验」。
- `workbook_progress_service.py` 旧逻辑三坑：只查 test、硬编码「先不发」、用旧 session pending 判待审；改后 prod 探针优先，改完需 `bash omdb/tgbot/restart.sh` 才生效
- 每日群进度须 **发群前 prod 验数门禁**；主人已多次强调，不能凭 session/测试库状态直接同步
- 发产卡在 `status=none`：让申请人（蓝猫）重提「申请发布」；审核人发产前仍须自跑 test T-1 对账，不以申请 PASS 代替实查
- [LESSON: workbook-progress,prod-check|群工作簿进度发群前必须 prod 实查分区/验数，禁止只看 test 或 dev session pending 状态]
- [LESSON: agent-bus,ack|并行处理私聊/工作簿时仍须 60 秒内 agent-bus ACK，核查完再 reply，禁止漏单]
- 群工作簿进度以 **prod 实查** 为准：prod 有近期分区即标「已完成」；不能只看 test、过期 dev session pending、或 work-log 流水（如 RP pending）
- 停留时长（#9）：prod `dws_session_duration_user_d` 7/31 首上，08-06 为 `is_valid=1` 补丁 + 补刷

