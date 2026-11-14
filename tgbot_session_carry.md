# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-15 · 最新归档：`sessions/tg-rotate-2026-11-15-0637.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 日报必须先跑双机同步（`prepare_daily_report_sync.sh`），确认 `hosts/new-mac` 与 `hosts/old-mac` 当日 work-log 齐全后再写稿，禁止只扫本机会话就交稿。
- 定稿后立刻 `post_daily_report_to_dm.py` 推 TG；对话里只确认「已推 + 路径」，禁止再贴全文（防双推）。
- 「上传云端」与推 TG 分离：主人未说上传前不要自动传；说了则用**主人改定后的正文**覆盖本地定稿后，原样跑上传脚本，_upload 前不改字。
- 主人改定日报后应对照初稿差异写 lesson，避免同类表述再犯（本会话：不宜把「等门禁」类外部卡点硬写进【死锁阻碍】）。
- 【今日结果】按金样句式：任务名 + 做了什么 + 结果 +「已完成」；进度型工作可写阶段性同步，勿凑条、勿写机器人名。
- 【死锁阻碍】/【专项复盘】默认留空；主人定稿里死锁为空时，表示当日无值得单列的内部死锁，不要因为「还在等门禁」就擅自填满死锁栏。
- 【明日动作】可带截止日（如周一），写真实续作 TOP1/TOP2（地区地图门禁恢复后发海豚日 SQL；归因渠道比对通过后日结与影子重建待命）。
- [LESSON: daily-report|【死锁阻碍】仅写当日明确应交未交的内部卡点；等门禁、等他人比对等外部依赖默认不写死锁，主人清空后须对照差异沉淀避免再硬塞]
- work-log 偏薄时，用本机 agent transcript、派单溯源（`task_provenance.jsonl` 等）与 bus 回执交叉核对，只计又初本人有交付的实活。
- 实时指标断流排查（prod 只读）：对比实时指标表停写时点与上游明细新鲜度；明细仍新、指标表自某时点停写 → 断点倾向实时写入作业，非上游明细。
- 主人授权 ≠ 绕过门禁**：即使授权 `dolphin_ops` 直发，平台会话门禁仍可能拦；先恢复 `pending` 或确认直发路径与门禁一致。
- 代点发布不可用**：他人 bot 代点「申请发布」若报 `No module named 'cursor_shared_session'`，走人工在平台点，勿指望 bot 闭环。
- [LESSON: 产发门禁|publish_request_status 被降成 none 而 reviewer/备注仍在时 i_can_publish_prod=false；须会话持有人 request-publish，审核人只审不发产自救]
- **产发 SQL 默认走平台**：MCP `publish-task-sql` 只支持 **test**；**prod** 用 `dolphin_ops` 或平台产发流程，且应带 `session_code`。
- **只发海豚、不扩 scope**：私聊明确「只发已有海豚任务」时，**不批**该会话 Spark 切流、**不挂**生产编排。
- **发前对齐仓库与现网**：以指定 commit（如 `6c85b3e3`）核对仓库日 SQL；再对比现网海豚同任务 SQL，确认缺口（本例：`order_mapped` 缺 `AND o.amount < 100000000`）。
- **发前安全窗口**：查目标工作流下次调度与 RUNNING 实例，无在跑且距触发有余量再发。
- **半截 publish 态**：`publish_request_status=none` 但审核人/备注仍在 → `i_can_publish_prod=false`，带会话的产发会被拒；**审核人不能自点「申请发布」自救**。

