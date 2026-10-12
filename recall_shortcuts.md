# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 10 12 2026 ads_channel_promotion_summ | `~/.dc-platform/memory/lessons/2026-10-12-ads_channel_promotion_summary_m-次留-口径.md` | 2026-10-12-ads_channel_promotion_summary |
| sql test 三列 仍跑旧 仓库 值三 | `sessions/tg-rotate-2026-10-12-2156.md` | 本地仓库 SQL 已对齐新口径时，**test 海豚若未重发**，仍跑旧 SQL |
| 不进 不进主键 主键 仍从 仍从渠道维表带出 从渠 | `sessions/tg-rotate-2026-10-12-2156.md` | **部门**仍从渠道维表带出，**不进主键**。 |
| 人数 先取 再对 再对周期取 周期 均活 | `sessions/tg-rotate-2026-10-12-2156.md` | **日均活跃**：先取**每日**渠道活跃人数，再对周期取**平均**。 |
| 人去 内渠 加总 单加 去重 周期 | `sessions/tg-rotate-2026-10-12-2156.md` | **新增**：周期内渠道新增**按人去重**，禁止把日新增简单加总。 |
| 「新 」不 三列 不同 不按 不按天加总」不同 | `sessions/tg-rotate-2026-10-12-2156.md` | 充值三列为**金额**，周期内**按天相加**即可；与「新增按人去重、不按天加总 |
| ads.ads_c ads.ads_channel_promotion_summ | `sessions/tg-rotate-2026-10-12-2156.md` | **结算充值**新增三列（周 / 月字段名成对）：VIP 订阅、扣量后 VIP、 |
| 「次 一天 不参 不参与次留 与次 业务 | `sessions/tg-rotate-2026-10-12-2156.md` | 周期**最后一天 / 业务日当天**没有「次日」，**不参与次留**（避免无次日 |
| app 交集 人数 仍挂在 任意 内任 | `sessions/tg-rotate-2026-10-12-2156.md` | **次留**仍挂在**注册渠道**行：注册日 D 的新增用户，与**次日同 Ap |
| app 「自 」一 一套 一行 仍是 | `sessions/tg-rotate-2026-10-12-2156.md` | 渠道推广**周表 / 月表**同一套口径；粒度仍是「自然周或自然月 × App  |
| 人去 内渠 加总 单加 去重 周期 | `sessions/tg-rotate-2026-10-12-2156.md` | 新增**：周期内渠道新增**按人去重**，禁止把日新增简单加总。 |
| app 不要 人数 人数记回注册渠道 仍走 内活 | `sessions/tg-rotate-2026-10-12-2156.md` | 次留不要求次日仍走注册渠道；**换渠道回来只要在 App 内活跃即算**，人数记 |
| ## 10 12 2026 agent_session_rotate app | `~/.dc-platform/memory/lessons/2026-10-12-次留-该渠道新增与次日全-app-活跃的交集-不要求回访仍在注册渠道-人数落在注册渠道行.md` | 2026-10-12-次留-该渠道新增与次日全-app-活跃的交集-不要求回访仍 |
| ## 10 12 2026 ads ads.ads_channel_promot | `~/.dc-platform/memory/lessons/2026-10-12-周月充值三列对-ads-ads_channel_promotion_summary_d-同期-s.md` | 2026-10-12-周月充值三列对-ads-ads_channel_promo |
| 一样 人去 仍按 仍按人去重 像金 像金额一样按日简单加总 | `sessions/tg-rotate-2026-10-12-1756.md` | **新增、次留、日均活跃**仍按人去重/既有口径，**禁止**像金额一样按日简单 |
| ads.ads_channel_promotion_summary_d mont | `sessions/tg-rotate-2026-10-12-1756.md` | 周月新增充值字段：`week_*` / `month_*` 与上三列一一对应；主 |
| coin_recharge_amount deduction_recharge  | `sessions/tg-rotate-2026-10-12-1756.md` | 日表三列金额（可跨天相加）：`recharge_amount`（VIP 订阅）、 |
| app dws.dws_settlement_detail order_paid | `sessions/tg-rotate-2026-10-12-1756.md` | 充值明细在 `dws.dws_settlement_detail`（`order |
| ads.ads_channel_promotion_settlement_sum | `sessions/tg-rotate-2026-10-12-1756.md` | 结算日汇总 `ads.ads_channel_promotion_settlem |
| 「部 」之 上筛 不会 之外 再拆 | `sessions/tg-rotate-2026-10-12-1756.md` | 按部门看数：在渠道行上筛选或汇总，**不会**再拆出「部门 × 渠道」之外的更细 |
| app_id dept_id dept_name dim.dim_channe  | `sessions/tg-rotate-2026-10-12-1756.md` | `dept_id` / `dept_name` 仅为渠道属性，**不进主键**； |
| app_id channel month_start_dt week_start | `sessions/tg-rotate-2026-10-12-1756.md` | 周表主键：`week_start_dt, app_id, channel`（分区 |
| ads.ads_cha ads.ads_channel_promotion_su | `sessions/tg-rotate-2026-10-12-1756.md` | 渠道推广周表 `ads.ads_channel_promotion_summar |
| app lesson 不要 不要求回访仍在注册渠道 与次 交集 | `sessions/tg-rotate-2026-10-12-1756.md` | [LESSON: 渠道周月表,次留口径/次留 = 该渠道新增与次日全 App 活 |
| ads.ads_channel ads.ads_channel_promotio | `sessions/tg-rotate-2026-10-12-1756.md` | [LESSON: 渠道周月表,ads_channel_promotion/周月充 |
| 一样 人去 仍按 仍按人去重 像金 像金额一样按日简单加总 | `sessions/tg-rotate-2026-10-12-1756.md` | 新增、次留、日均活跃**仍按人去重/既有口径，**禁止**像金额一样按日简单加总 |
| ## 10 11 200 2026 agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-11-用户要求重新打卡时先查计划窗口再补打-接口短暂断开时在窗口内依赖调度重试-成功回执须含北京时间-.md` | 2026-10-11-用户要求重新打卡时先查计划窗口再补打-接口短暂断开时在窗口 |
| set_leave_day skip 「重 上班 不应 不应混 | `sessions/tg-rotate-2026-10-11-0655.md` | 周六若仍有上班计划（值班/未 skip 日历），补打逻辑与工作日相同；请假日应走 |
| jst onehr 一用 一致 京时 动包 | `sessions/tg-rotate-2026-10-11-0655.md` | 启动包里的时区若写 JST，对外汇报打卡时间统一用**北京时间**，与 OneH |
| retry 下一 主人 人介 介入 入的 | `sessions/tg-rotate-2026-10-11-0655.md` | 回执用结果向短句：成/未成、时间点、若失败则下一 retry 或需主人介入的条件 |
| launchd onehr 「查 一套 人工 人工触发时同样走「查窗口 | `sessions/tg-rotate-2026-10-11-0655.md` | 私聊补打卡与 launchd 自动打卡是同一套 OneHR 链路；人工触发时同样 |
| 16） 19 schedule 下班 为全 仍按 | `sessions/tg-rotate-2026-10-11-0655.md` | 补打成功后顺带说明下班卡仍按原计划（如 19:16），避免用户误以为全天 sch |
| 09 50 52 56 「接 」多 | `sessions/tg-rotate-2026-10-11-0655.md` | 09:50、09:52 等「接口断开」多为瞬时故障；只要在计划窗口内，调度重试仍 |
| 200 http onehr 上传 上班 上班卡成功以 | `sessions/tg-rotate-2026-10-11-0655.md` | OneHR 上班卡成功以 HTTP 200 为准；回执里应写清北京时间、是否通过 |
| 「现 」时 上班 不要 不要只复述失败原因 与计 | `sessions/tg-rotate-2026-10-11-0655.md` | 用户说「现在重新打卡 / 补打上班卡」时，先查当日打卡入口与计划窗口，再立刻执行 |
| ## 10 2026 agent_session_rotate calendar | `~/.dc-platform/memory/lessons/2026-10-10-问-几点打卡-须先查当日-cn_punch_calendar-用北京时间报上下班计划-并分开说明.md` | 2026-10-10-问-几点打卡-须先查当日-cn_punch_calenda |
| jst 上下 下文 东京 东京时间 为准 | `sessions/tg-rotate-2026-10-10-0955.md` | 用户侧上下文若写 JST/东京时间，对外报打卡仍以**北京时间**为准，避免时区 |
| 09 50 52 不必 不必让用户立刻重复手打 会在 | `sessions/tg-rotate-2026-10-10-0955.md` | 若刚试过打卡但接口断开（如 09:50、09:52 连续失败），应说明失败原因  |
| 「卡 「计 」和 上」 上要 为已 | `sessions/tg-rotate-2026-10-10-0955.md` | 同时区分「计划打几点」和「卡是否已打上」；未打上要单独说明，避免用户以为已经打卡 |
| eh hr ne on 上班 下班 | `sessions/tg-rotate-2026-10-10-0955.md` | 标准答复：用**北京时间**给出**上班**、**下班**两个计划时刻（OneH |
