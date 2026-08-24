# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-24 · 最新归档：`sessions/tg-rotate-2026-08-24-1918.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 此类错误与**模型额度用尽**、`unavailable for your plan` 等 quota 问题要分开看，勿混为一排查
- 用户问「为什么一直失败」时，多半是同一会话反复 hit 失效 resume；Bot 已自愈清 resume，**不需要再查业务根因**
- （已有 lesson「传输故障 vs 业务逻辑」「轮换前先沉淀」，本条无新增铁律，不硬写 LESSON。）
- TG 私聊报「Cursor 会话连接失败」属于**传输/会话层**故障，不是业务 SQL、ETL 或派单逻辑错
- Bot 检测到 `failed to connect/resume`、`session expired/invalid` 等模式时，会**自动丢弃失效的 `cursor_chat_id`（旧 resume）**，避免下一条继续 `--resume` 卡死
- 用户侧标准恢复：**原句重发**即可（resume 已清，下一条会新开 Cursor 会话）；或发 **「重启 agent」** 强制轮换
- 「重启 agent」会走 `rotate_workspace_session`：杀僵 agent、清 in_progress、强制新开共用会话，并 TG 通知
- 队列里任务可能**积压很久**才跑并失败（Cursor 侧卡住），看起来像「没干活」，实为基础设施瞬时故障
- 历史上 #283/#284、#329、#394 等同模板失败，事后验证多为 Cursor 云端/API **瞬时不可达**，恢复后私聊可通
- 共用 resume 过长会触发定时/阈值轮换（日切、transcript 体积）；轮换前应先**记忆沉淀**再清 resume
- 私聊秒回类（在吗、寒暄）不进完整 Agent 链；本条是 Agent 正式处理后的**固定失败模板**，不是秒回
- 失败模板刻意简短：告知已清 resume + 两条恢复路径，避免把传输错误包装成业务答复
- 向工作狂人转交指标库设计时，应打包主稿、配套门禁稿、DDL 草案三份，正文写清各自用途，并指明审阅入口（如主稿 §10.1），便于对方直接开审
- 对照已钉约束（不做 Headless BI、AI 只 propose、挂已有 DWS/ADS 列、同名拆条、禁比率进 canonical、published 要 req_ref、先治 264 条脏库），最贴方案是 **以 Metric Store 为核的轻量 Semantic Layer**（≈ dbt MetricFlow 路线）
- [LESSON: metric-library-design|改指标库表结构前先定理论层次（Registry / Metric Store / Semantic Layer），对照业务约束选「Metric Store 为核的轻语义层」，勿默认纯登记表或全量 Ontology]
- [LESSON: metric-library-governance|知秋在 v0.2 底座 vs v0.3 超集拍板前，禁止改 DDL、建表或按未定增量落库]
- 指标模型理论可粗分五派：维度建模/指标集市、Metric Store、Semantic Layer、Ontology、Context Layer；讨论前先定「做到哪一层」，再动表结构
- 现稿 `metric_concept / label / implementation` 定位是 **Metric Store + 轻语义壳**，是 metric core 草稿，不是完整指标模型

