# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-17 · 最新归档：`sessions/tg-rotate-2026-08-17-1044.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 狂人派单若带 **Q1/Q2/Q3** 或「不许跳过三问」，回执必须**逐条按模板填**；报运行态、test 有 bucket0、或「已完成/待命/rest」**不算答复**。
- 含 **HOLD、打回、三问、口径争议** 的 bus **禁止走快车道** `reply_only` 自动「待命/rest」结案；应进 Cursor 主会话按格式交作业。
- session_duration bounce 争议根因**：08-04 `a17b55f6` 改为仅 `is_valid=1` 进 DWS，与知秋 07-21「bounce 第 0 档」冲突；开发侧自行解读 PRD，**未与产品书面确认**（Q1=没确认过）。
- Q3 铁律**：产品未拍板前开发**不能代决**；选项 (a) 维持无 bucket0 或 (b) bounce 进第 0 档并重跑 45 天；**45 天 prod 重跑继续 HOLD**。
- 口径争议项工作簿/周报应标 **HOLD · 等产品拍板**，禁止标「已完成」；DDL COMMENT 补丁可先行，不等同口径结案。
- [LESSON: agent-bus,worker_ant,口径争议|狂人 bus 含 Q1/Q2/Q3 或「不许跳过三问」时禁止快车道 reply_only 结案，必须进主会话逐条填三问后再 reply]
- [LESSON: session_duration,bounce,datacheck|prod 有分区有数不能证明口径对；bounce 争议看 DWM is_bounce 与 DWS bucket0/bounce_cnt 是否对齐，未拍板前标 HOLD、禁 45 天 prod 重跑]
- **表在跑、分区有数 ≠ 口径正确**；口径争议（如 bounce 是否进 DWS）须单独正面答，不能拿 prod 有数据当结案依据。
- 快车道误结案后：原 bus 已 closed 时，补发须用 `agent_bus_send.py --no-dedup` 发新 reply（如 bus#6588），否则 dedup 会挡掉。
- **session_duration bounce 争议根因**：08-04 `a17b55f6` 改为仅 `is_valid=1` 进 DWS，与知秋 07-21「bounce 第 0 档」冲突；开发侧自行解读 PRD，**未与产品书面确认**（Q1=没确认过）。
- 仓库/指标库/平台**均无 PRD v1.0.2 §5.5.4 逐字原文**；现有表述只写 `<5s/>12h 不进 DWS`，**未写清 bounce 是整表排除还是单独计 bounce_cnt**——这是 08-04 误读来源（Q2）。
- **Q3 铁律**：产品未拍板前开发**不能代决**；选项 (a) 维持无 bucket0 或 (b) bounce 进第 0 档并重跑 45 天；**45 天 prod 重跑继续 HOLD**。
- prod 复验判据：DWS `bucket0=0`、`bounce_cnt=0`，但 DWM `is_bounce=1` 有量（如 08-14 约 856 万）——争议在**口径分层**，不是表没跑。
- 狂人同一要求多轮（#6556→#6573→#6586）仍须当**未结案**处理，直到 Q1/Q2/Q3 正式发出；私聊追问说明 bus 侧已误结案，须立刻补发而非再报状态。
- 周报（W33 范式）：自然周 + 有效工作日、分专项【本周完成/卡点/下周计划】、口径争议写「test 验通但 prod 冻结 HOLD」、P0 卡点单列产品拍板项。
- 蓝猫** = 数据开发同学（如内容排行、停留时长等）；**野花** = 另一类 dev session 审核人；角色分工勿与文档配色混写
- 主人说「需要排版的就催」→ 仅对 **等审核/排版** 项催办：**bus 私催审核人 + 协作群 @**，正文带 **bus#、dev session code、test 验数结论**
- 日报「已完成」只写当日真有交付闭环的项；**本地定稿待上传** 应放「明日动作」，勿与已上平台项混标完成

