# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-29 · 最新归档：`sessions/tg-rotate-2026-08-29-1554.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 狂人 #201 卡点：**数据层**（published=0、G4 空跑），不是 v0.3 结构层；解法是推已齐门禁的样例，不是改表结构。
- 260 条 draft 缺 `definition`/`req_ref`：**禁止**批量改 lifecycle；要上 published 须 P1 补齐再迁。
- 样例推送 SQL：`docs/metric_library_phase1_publish_samples_20260829.sql`；修完 bus 报三数请对方只读重验（#7602 → #7603 PASS）。
- G5 分两层**：库内 `diverged_pending` 且 `is_primary` 违规可为 0；**应用层**门禁（service/router 做 G4/G5 validate）当时**未落地**，勿混为一谈。
- 库内尚有 `avg×2`、`count_distinct×4` 同类禁项：须对方点头后再清，勿擅自批量改。
- [LESSON: metric-library,derived,ratio,whitelist|derived 比率指标禁止 `default_aggregation=ratio`；按 v0.3 白名单留空 agg，用分子/分母 FK 表达比率]
- Phase1 过关 ≠ 只灌 draft：test 上须真有 `lifecycle=published` 且逐条满足 G4，API 才能切概念层。
- 推 published 前先真 COUNT：`published / draft / orphaned`（本轮：10 / 260 / 10，库 `172.31.6.193/metadata`）。
- **G4 四件套**：`definition` + `req_ref` + ≥1 active impl + 白名单 `default_aggregation`；另核 **G7-a**：`entity_code`、`main_event_code`、`time_window`。
- Unblock 二选一：P1 迁存量，或先推 **Phase1.5 种子 10 条**（`seed:phase1.5`，如 `user_register_cnt` 等）。
- **G5 分两层**：库内 `diverged_pending` 且 `is_primary` 违规可为 0；**应用层**门禁（service/router 做 G4/G5 validate）当时**未落地**，勿混为一谈。
- **ratio 口径（v0.3 §11）**：白名单仅 `sum/count/bitmap_union_count/max/min`；**不含** `ratio`/`avg`/`count_distinct`。
- 比率类指标：`metric_kind=derived` + 分子/分母 FK；`default_aggregation` 应**留空**，不能写 `agg=ratio`（含已 published 的 `order_paid_rate`）。
- 已清 12 条 derived 的 `agg=ratio`：`docs/metric_library_phase1_clear_derived_ratio_agg_20260829.sql`；FK 保留。
- 「注册事件」在脏表里事件名是 **`user_register`**，不要未经核对就混写 `register` / `user_register`。
- 第一遍 SQL 列名/事件名写错时，**立刻改 SQL 重查并交付**，不要只解释或重复「在查」；被问「变傻了」时简短认错 + 说明已修正即可。
- [LESSON: paimon,dirty_data,sql|查 `dwd_standard_dirty_data_df` 前先对元数据，禁用臆测列（如无 `create_time`）；注册事件用 `user_register`，勿混 `register`]
- 查 **Paimon 脏表**（`paimon.dw.dwd_standard_dirty_data_df`）前，**先对元数据/列名**再写 SQL；该表**无 `create_time`**，可用 `process_time`。

