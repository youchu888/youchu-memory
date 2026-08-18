# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-18 · 最新归档：`sessions/tg-rotate-2026-08-18-2130.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 狂人 bus#6676 U1~U7 评审结论：三层 concept/label/implementation 方向对；staging + 5 条门禁可挡 U5；**MySQL 8 无部分索引时用生成列 NULL 不参与唯一**（`primary_slot`/`biz_term_key`）实现条件唯一
- 设计稿补充铁律：`orphaned` 仅 implementation 层派生禁双写；G6 复核队列 + `v_metric_impl_candidate_rejected_review`；**granularity 是 concept 固有属性**；`diverged_since`/`diverged_owner` + 7 工作日 SLA
- [LESSON: metric-library|DDL 评审后改稿 push 不等于建表；Phase0 test DDL 须等 5 条拍板 + 知秋别名真源/lifecycle 两项，禁止抢跑]
- 指标库分「概念设计 v0.2」与「现网 metadata 存量」两条线；设计交付 ≠ 可发布口径库，264 条存量仍处止血态治理阶段
- 概念层设计三件套：`metric_library_concept_model_v0.2`、`metric_library_system_v0.2`（#6552 四件套/75 条拆条流）、`metric_library_concept_model_ddl_draft`（旁路四表，**未执行**）
- 又初侧设计闭环后仍须等外部拍板 5 项（test Phase0 建表、别名真源、264 条 lifecycle 批量改、derived 存法、是否与 Phase2 并行）才能动 DDL / dev-session
- 现网 `metric_standard` 快照：264 条；175 有 formula；**75 条同名多实现**是 Phase2 拆条输入；89 仍缺 formula；27 绑定软下线
- 跨角色协作：设计交 bus#6662/#6664 给知秋/狂人；超时无回执用 bus#6673 合并催办，材料固定指向 `origin/dev` commit + 三份文档路径
- DDL 硬伤定案（commit `4d15c1ed`）：`metric_label` 改 `UNIQUE(concept, kind, text)` + `label_primary_slot`；去掉 `canonical_code`；legacy 解析须带 `table_fqn`，多条命中 **409 消歧**
- 狂人点头改稿后 Phase2 语义归纳（75 条拆条、U1/U3 优先）可启动；**test/prod DDL 与现网写操作仍等知秋两项拍板**
- 大漏斗 test 建表：表 `dws.dws_app_event_funnel_d_d`（test SR）；DDL 源 `ops_system/04.dws/dws_app_event_funnel_d_d/`；须绑 dev session `dev-20260807-big-funnel-001` 经 MCP `db.run_ddl_etl` 执行
- 大漏斗宽表结构：主键 `(dt, app_id, is_new)`；18 事件 × 3 指标 = 54 列；动态日分区近 30 天～未来 3 天；建完表为空，日批走 Spark/Paimon 另链路
- Paimon/staging（如 `dws_app_event_funnel_metric_stg_d`）不在 SR DDL 一步搞定；需在 Hadoop 跑 `run_paimon_ddl.sh`，与 SR 宽表分开交付说明
- 停留时长口径要分层**：**有效会话规则**（无 bounce、墙钟 <5s 或 >12h 剔除）与 **离开事件埋点**（单页测不出时长）是两件事，对外回执、工作簿、memory 均须分开写，禁止揉成一句「问过/没问过」。
- 工作簿「今天只报今天的事」**：近况优先读**当日 work-log 实活**（「已做」以「今日：…」开头），不要每天复读旧 bus 挂账、硬编码「已知事实」或固定卡点套话（如「45 天重跑仍冻结」）。
- 状态类词（已完成/HOLD/没问过）发前须实查**：代码逻辑、session、prod 分区、bus 结案是否真对齐，禁止凭印象或旧模板。
- [LESSON: workbook,tgbot|工作簿进展读当日 work-log 实活，禁捞旧 bus 挂账与每日重复模板；今天确认清楚再回，明天再报明天]
- **停留时长口径要分层**：**有效会话规则**（无 bounce、墙钟 <5s 或 >12h 剔除）与 **离开事件埋点**（单页测不出时长）是两件事，对外回执、工作簿、memory 均须分开写，禁止揉成一句「问过/没问过」。

