# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-14 · 最新归档：`sessions/tg-rotate-2026-11-14-0608.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主人授权 ≠ 绕过门禁**：即使授权 `dolphin_ops` 直发，平台会话门禁仍可能拦；先恢复 `pending` 或确认直发路径与门禁一致。
- 代点发布不可用**：他人 bot 代点「申请发布」若报 `No module named 'cursor_shared_session'`，走人工在平台点，勿指望 bot 闭环。
- [LESSON: 产发门禁|publish_request_status 被降成 none 而 reviewer/备注仍在时 i_can_publish_prod=false；须会话持有人 request-publish，审核人只审不发产自救]
- **产发 SQL 默认走平台**：MCP `publish-task-sql` 只支持 **test**；**prod** 用 `dolphin_ops` 或平台产发流程，且应带 `session_code`。
- **只发海豚、不扩 scope**：私聊明确「只发已有海豚任务」时，**不批**该会话 Spark 切流、**不挂**生产编排。
- **发前对齐仓库与现网**：以指定 commit（如 `6c85b3e3`）核对仓库日 SQL；再对比现网海豚同任务 SQL，确认缺口（本例：`order_mapped` 缺 `AND o.amount < 100000000`）。
- **发前安全窗口**：查目标工作流下次调度与 RUNNING 实例，无在跑且距触发有余量再发。
- **半截 publish 态**：`publish_request_status=none` 但审核人/备注仍在 → `i_can_publish_prod=false`，带会话的产发会被拒；**审核人不能自点「申请发布」自救**。
- **解半截态**：须 **会话持有人**（如蓝猫）在开发平台再点「申请发布」，审核人监视到 `pending` 后再发产。
- **主人授权 ≠ 绕过门禁**：即使授权 `dolphin_ops` 直发，平台会话门禁仍可能拦；先恢复 `pending` 或确认直发路径与门禁一致。
- **产发闭环**：发完私聊/ bus 通知相关人（本例通知蓝猫）；补数日期（11-03/10/11）由主人另行安排，不与发 SQL 混做。
- **代点发布不可用**：他人 bot 代点「申请发布」若报 `No module named 'cursor_shared_session'`，走人工在平台点，勿指望 bot 闭环。
- TG/Cursor 派活带大 `prompt_*.md` 时：先读启动包，再通读该文件并定位末尾「当前问题」；按问题执行，禁止只复述 prompt。
- 对同一 `reply-to-bus-id` 的实质回执若被出站去重拦截，可用 `--no-dedup` 重发；仍须带可查证的核数结论，勿空「已知悉」。
- 运维回执类任务（如「alter 六句已执行」）：出口统一走 `agent_bus_send.py`，`--reply-to-bus-id` 对齐原派单（如 bus#13263），结案用 `kind=reply`。
- SR 影子表 DDL 完工回执前：prod 只读轻量验收——列总数 + 目标列名与列序，再发 bus；必要时附 `SHOW CREATE TABLE` 或等价列清单。
- 本例验收表：`dws.dws_register_attribution_result_d_paimon_shadow`；六列为 `score_brand / score_model / score_system / score_system_version / score_time / time_bucket_max_seconds`（与 35 列总量、列序一并核对）。
- 正文对外写业务主人名（知秋），技术上记清新 outbound bus id（如 #13275）与所回复 bus id 的对应关系，便于对账。

