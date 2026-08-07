# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-07 · 最新归档：`sessions/tg-rotate-2026-08-07-2244.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- `workbook_progress_service.py` 旧逻辑三坑：只查 test、硬编码「先不发」、用旧 session pending 判待审；改后 prod 探针优先，改完需 `bash omdb/tgbot/restart.sh` 才生效
- 每日群进度须 **发群前 prod 验数门禁**；主人已多次强调，不能凭 session/测试库状态直接同步
- 发产卡在 `status=none`：让申请人（蓝猫）重提「申请发布」；审核人发产前仍须自跑 test T-1 对账，不以申请 PASS 代替实查
- [LESSON: workbook-progress,prod-check|群工作簿进度发群前必须 prod 实查分区/验数，禁止只看 test 或 dev session pending 状态]
- [LESSON: agent-bus,ack|并行处理私聊/工作簿时仍须 60 秒内 agent-bus ACK，核查完再 reply，禁止漏单]
- 群工作簿进度以 **prod 实查** 为准：prod 有近期分区即标「已完成」；不能只看 test、过期 dev session pending、或 work-log 流水（如 RP pending）
- 停留时长（#9）：prod `dws_session_duration_user_d` 7/31 首上，08-06 为 `is_valid=1` 补丁 + 补刷
- 页面访问（#10）：prod `dws_app_page_visit_d_d` 日批约 71 万行；`dev-20260804-002` 已 approved；`wf_dws_汇总_日` 05:25 跑，T-1 `etl_time` 可对齐
- prod/test 对账：test 为稀疏采样，**不能逐行对 prod**；回执写 prod 分区行数/PV/UV + 调度时间即可
- agent-bus 与私聊并行：处理 A 时不能漏 B；**60 秒内 ACK**，再逐项核查 reply 结案（bus#6106 先例）
- 订单发产（`dev-20260728-ura-001`）：test 就绪 ≠ 可发产；须 `publish_request_status=pending` 且 `publish_reviewer_id=指定审核人`，否则 `i_can_publish_prod=false`、按钮不亮
- 日报：先跑 `prepare_daily_report_sync.sh` 双机同步；定稿原样上传云端；工作簿进度修复、订单发产跟进等运维项**默认不写**今日结果/明日动作
- 知秋派单回执要点：页面访问 prod 验数、session 分工、channel_summary 双扫仅跨日界（3h 迟到补偿待拍板）、设备标签重复 session 建议留 002 关 001
- 写日报铁序：**先核查 prod/test/平台与流水，再落稿**；禁止凭印象或局部样本先写后改。
- 报补数范围/耗时时须查**全部分区** `etl_time` 与海豚 PI，禁止只看最近几天（曾把 36 天/72 秒误写成 5 天/7 秒）。
- 日报读者是部门/主管：用通俗业务话（约 40～70 字/条），**禁止**分区号、PI#、`etl_time`、裸表名等内部核对细节进正文。
- 日报被主人定稿后，上传云端须**原封不动**用给定正文，禁止改写后再传。
- [LESSON: daily-report,datacheck|写日报前必须先 prod/test/平台逐项核查再落稿，状态与补数范围禁止凭印象或局部样本]

