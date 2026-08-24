# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-24 · 最新归档：`sessions/tg-rotate-2026-08-24-1836.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 向工作狂人转交指标库设计时，应打包主稿、配套门禁稿、DDL 草案三份，正文写清各自用途，并指明审阅入口（如主稿 §10.1），便于对方直接开审
- 对照已钉约束（不做 Headless BI、AI 只 propose、挂已有 DWS/ADS 列、同名拆条、禁比率进 canonical、published 要 req_ref、先治 264 条脏库），最贴方案是 **以 Metric Store 为核的轻量 Semantic Layer**（≈ dbt MetricFlow 路线）
- [LESSON: metric-library-design|改指标库表结构前先定理论层次（Registry / Metric Store / Semantic Layer），对照业务约束选「Metric Store 为核的轻语义层」，勿默认纯登记表或全量 Ontology]
- [LESSON: metric-library-governance|知秋在 v0.2 底座 vs v0.3 超集拍板前，禁止改 DDL、建表或按未定增量落库]
- 指标模型理论可粗分五派：维度建模/指标集市、Metric Store、Semantic Layer、Ontology、Context Layer；讨论前先定「做到哪一层」，再动表结构
- 现稿 `metric_concept / label / implementation` 定位是 **Metric Store + 轻语义壳**，是 metric core 草稿，不是完整指标模型
- 现稿缺口：entity、合法切片/join 路径、适用范围与认证态、req_ref/owner/血缘/策略等上下文、指标间可推理的业务关系
- 2025–2026 对外主流叫 **Semantic Layer**；可执行内核多数是「Metric Store + 一点 entity/维度语义」，不是纯登记表也不是全量本体
- 纯维度集市不够（痛点是口径治理与多实现）；纯 Metric Registry 偏轻；全量 Ontology 过重；完整 Context Layer 宜中期挂接、首刀不重造
- 建议三层分工：A 轻本体（业务对象与关系）→ B 语义/指标核心（entity、维度、指标、派生、时间语义、认证）→ C 上下文治理（req_ref、owner、血缘、质量、策略、发布态）；中期以 B 为主，C 只绑定现有能力
- 与狂人 v0.3 同族：都走 semantic layer / MetricFlow 侧；立场一致；v0.2 三层是底座，v0.3 在其上加 entity/event/role 为超集
- 知秋待拍板二选一：A 仅保留 v0.2 三层底座，或 B 走 v0.3 综合方案（三层保留）；**拍板前不改 DDL、不建表**
- 画 ER 时：v0.2 三层作实线底座，v0.3 增量（entity/event/role）用虚线标注「待拍板」，避免把未定方案画成已定
- 三方对齐流程：主人定倾向 → 理论调研收讨论稿 → bus 狂人 → 狂人转知秋 → 回执对齐关系 → 知秋拍板后再改设计稿/DDL
- 页面访问 YC-PV-001**：「进入」需有来路；访问次数可高于跳转属正常；跳出率公式已定稿不会负值；测试对账后发产并补近月分区。
- [LESSON: tgbot|绿点|打卡|问机制先读 `should_appear_online()` 与计划时间生成，勿把 `JIKE_CHECKIN_ENABLED` 当成绿点开关]
- [LESSON: 周报|work-log|双机|hosts 缺口须在周报正文标注，勿假装双机流水齐全]
- **TG 绿点与极客打卡解耦**：`JIKE_CHECKIN_ENABLED=false` 只关真实打卡；计划上下班时间仍会生成，绿点跟计划走，不跟签到状态。

