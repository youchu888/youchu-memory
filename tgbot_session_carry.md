# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-13 · 最新归档：`sessions/tg-rotate-2026-08-13-1229.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 口语里的「搜索引擎占比」在数仓**没有同名现成指标**；先查元数据/字段，不要默认有 baidu/google/bing 标准口径。
- 口径不确定时，**先 agent-bus 找业务方拍板**（是否等于 organic、是否有 SEM/外链数据源），再定稿对外结论。
- 看板两页数字不一致，先**分别对齐底层表和 API**，不要先假设业务口径不同。
- 「用户活跃」若仍走废弃 **V1** `/user/active/trend`，只计 PV（`dau_ids`），**不含当日纯注册未浏览用户**；核查必须用 V2。
- [LESSON: db,SEO,organic|「搜索引擎占比」无标准字段时，用自然新增占比作临时代理并 bus 确认业务定义，禁止把站内搜索或渠道 0 当结论]
- 关键词相关表统计的是**站内搜索**，不能当作外链搜索引擎流量占比。
- 按渠道名匹配 baidu/google/bing 等，T-1 这批 SEO 项目**全为 0**时，应立刻怀疑口径不对，而不是硬报 0。
- 最接近的代理口径是**自然新增占比**：`new_reg_nature_count / new_reg_count`（`channel=organic`），来源 `ads.ads_product_day_stat_d`。
- 批量查多项目 SEO 占比时，固定对齐 **app 编码 + T-1 + prod**，并同时给「单项目自然占比」和「组合内近 7 天份额」。
- YC-001 活跃账号数可对齐链路：`ads_product_day_stat_d.dau_count`、`dws_app_user_d.active_users`、`ads_app_metrics_daily_d`，以及 `/product/report/daily` 与 `/user/active/v2/*`。
- **日批跑完后**上述来源应一致；若白天看到 13.8 万 vs 7.8 万，优先查**分时累计活跃快照时刻**，不是定义冲突。
- 8.12 分时累计活跃典型轨迹：约 11:00 ≈ 7.8 万、21:00 ≈ 14.0 万、全天 ≈ 16.0 万；一个页面走实时/小时累计、另一个仍停较早时刻或未出完离线日表，就会出现「同日期两数」。
- 离线日表通常在**次日早上**才稳定；复验不一致要记录**查看时间、筛选条件、接口版本**。
- 群聊显式 @ 又初/初儿/@youchu_ai_bot 时，必须在群里给**实质答复**；禁止以「没@本机器人/群里不回」推辞。
- 大漏斗 session `dev-20260807-big-funnel-001` stage3：Spark 两阶段 ETL（metrics+wide）已跑通，SF-81 dt=2026-08-03 冒烟 spot-check PASS；开发侧卡点清完后等**集群全 app 压测**再补 stage4。
- 主人说「数据有问题/停了吧」→ **立刻 kill** YARN 任务并清本地 `run_yarn_daily_sql` 残留进程，再自查；未查清前不要重 submit。
- 说「你自己先查啊」= 不要等狂人回，主动查上游：SR 量级/小时分布、湖仓分区可读性、Flink fanout schema。
- 2026-08-11 停跑根因：Paimon **schema-6 事故**——`dwd_user_register_d_v2_r` 重建后 Flink fanout 仍写旧 schema，register 分区仅 ~8% 且不可读；video/novel/comic 同 fanout，湖侧整体不可靠；治本需重启 Flink fanout，狂人拍板前不再 submit。

