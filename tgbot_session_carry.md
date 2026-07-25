# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-25 · 最新归档：`sessions/tg-rotate-2026-07-25-1624.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 本地 ETL 合表（4→2、`stat_grain=session|daily`）后，必须同步 dev session：outputs、related_tables、DDL/ETL、task.yaml；平台可能仍停旧结构，以 API 推 v2 为准
- test 闭环顺序：海豚发布 v2 task → 补跑 PI 成功 → T-1 验数 PASS → `request-publish` 绑 reviewer → 再通知审核
- 口径争议以 **prod 海豚线上 SQL** 为准，勿只看仓库；用户订单模型 `region` 用 `dim.dim_user_all` 注册地区（方案 A），非订单事件 IP/地理
- 星型六原则：事实优先、每源每 biz_dt 单次扫描、dim JOIN 克制、度量分型（UV 用 bitmap）、禁 SUM(日 UV)、列卫生
- 交付根因/修复建议 HTML **不等于** 已执行配置变更；查开通状态要同时看配置表、`result_d` 行数、注册埋点 `attribution_flag`
- [LESSON: dev-session|本地合表/改 outputs 后立刻用平台 API 同步 session，勿假设插件已跟上]
- [LESSON: collaboration|提审 @ 审核人用 `@mudan99_bot`（野花），禁止 @ 主人代审]
- 子 session 的 design/memory 会重定向父 session，改设计文档前先确认目标 session，误改父文档用 git 恢复再推平台
- 旧 daily task 平台 delete API 404 删不掉时，在提审材料里注明待人工下线；不影响 v2 两 task 出数
- 群通知审核人须 @ 正确对象：主人 `@youchu8888` ≠ 审核人野花；野花是 `@mudan99_bot`（牡丹），审单走开发平台 pending
- 上线前核查除群 @ 外，应用 agent-bus 私信审核人，写清 session、合表口径、test 版本、验数 dt、待下线项与开放项
- 星型建模（v3.3）：中心宽事实（dws/ads）+ 少量共享 dim（用户/日历/地区）+ 展示属性作退化维 inline；rank/占比查询层算，不落表
- 先判范式：汇总报表走星型 checklist；当前态标签、uid×dt 明细、LTV cohort 不是星型，别硬套
- stage 2 写 `design.md` 前先读 `.claude/database/playbooks/star_schema_design.md` 的 checklist
- JHG 归因开通需 **两步**：`dim.dim_app_attribution_config` 插 `is_run=1` **且** 客户端注册带 `attribution_flag:1`；缺任一 `result_d` 仍为 0
- 两条 DWS **禁止**把 page_stay 与五档时长硬并表：粒度（有无 uid）、主指标（valid_stay vs 墙钟五档）、典型用法（导出/对账 vs 看板柱状图）都不同；`division_alignment.md` 已划界「禁止重复聚合同一指标」
- 五档合表核心判别列：`stat_grain`（`session`=单次五档，`daily`=日均五档）；同名 `duration_bucket` 语义不同，查询/接口必须带 `WHERE stat_grain=...`
- test 改 PK/删表：`my.cnf.test` 的 dc_admin **对 dws 无 DROP**；建删表迁移用 **test root `@43.212.113.132:9030`（无密码）**，不要推给主人手工跑

