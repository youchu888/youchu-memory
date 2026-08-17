# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-17 · 最新归档：`sessions/tg-rotate-2026-08-17-1644.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- AI 批量生成的列级血缘**未经人工复核**，上线前必须对照现网海豚 task SQL 逐列核对，错了会误导影响分析。
- 机器核对已覆盖表级拓扑（FROM/JOIN 双向比对）：106/123 一致、0 差异时，**不要再花时间验「上游是不是那几张表」**。
- 周报「说人话」**不等于**改成日报结构；保留原周报版式（`### 专项分块`、`【卡点】`、下周表格、日报索引、「一句话给周会」），只改措辞。
- 周报正文去掉 `stage3`、`v189`、`bucket0`、`agent-bus`、`poller` 等内部说法，换成业务部门能直接听懂的表述；状态写「已完成」，不写「进行中」。
- 周报汇总口径：正式日报 + 双机 work-log 合并稿 + `hosts`；`new-mac` / `old-mac` 缺流水要**如实点明**，不假装双机齐全。
- 「一句话给周会」也要说人话：上周交付、当前卡点、本周动作各一句，方便复制进周会。
- 血缘核对 fallback：海豚元库连不上时，用 MCP 拉 live task SQL 做人工抽查，详报落 `.claude/database/reports/lineage_<bus>/`。
- 停更旧表 + 新表并行时（如 `dws_user_tag_d` vs `dws_user_tag_d_d`）：以**现网在跑 task 的目标表和 FROM/JOIN** 为准，旧表应 deprecated、为新表重建血缘。
- 列级血缘错不只来自源表选错：`WHERE` 过滤（如 `is_valid=1` 滤掉 bounce）会导致聚合列（如 `bounce_cnt`）与血缘描述不一致，prod 未发版时仓内 SQL 已对也仍算问题。
- prod 表可能是 **VIEW** 而非物理 INSERT，核对要先确认架构，不能按普通写入 task 套。
- 人工核对重心转到机器做不出的列级四类：同名列归属（JOIN 多表时的 `app_id`/`dt`/`channel`/`uid`）、WHERE 过滤、聚合口径、视图/停更表等特殊架构。
- 狂人派单若带 **Q1/Q2/Q3** 或「不许跳过三问」，回执必须**逐条按模板填**；报运行态、test 有 bucket0、或「已完成/待命/rest」**不算答复**。
- 含 **HOLD、打回、三问、口径争议** 的 bus **禁止走快车道** `reply_only` 自动「待命/rest」结案；应进 Cursor 主会话按格式交作业。
- session_duration bounce 争议根因**：08-04 `a17b55f6` 改为仅 `is_valid=1` 进 DWS，与知秋 07-21「bounce 第 0 档」冲突；开发侧自行解读 PRD，**未与产品书面确认**（Q1=没确认过）。
- Q3 铁律**：产品未拍板前开发**不能代决**；选项 (a) 维持无 bucket0 或 (b) bounce 进第 0 档并重跑 45 天；**45 天 prod 重跑继续 HOLD**。
- 口径争议项工作簿/周报应标 **HOLD · 等产品拍板**，禁止标「已完成」；DDL COMMENT 补丁可先行，不等同口径结案。
- [LESSON: agent-bus,worker_ant,口径争议|狂人 bus 含 Q1/Q2/Q3 或「不许跳过三问」时禁止快车道 reply_only 结案，必须进主会话逐条填三问后再 reply]
- [LESSON: session_duration,bounce,datacheck|prod 有分区有数不能证明口径对；bounce 争议看 DWM is_bounce 与 DWS bucket0/bounce_cnt 是否对齐，未拍板前标 HOLD、禁 45 天 prod 重跑]

