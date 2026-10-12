# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
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
| 「查 」流 一套 一定 上班 不打 | `sessions/tg-rotate-2026-10-10-0955.md` | 周六若有上班安排，仍走同一套「查日历 → 报计划 → 报实际/重试状态」流程，不 |
| should_skip_punch 「今 一致 上下 下班 不要 | `sessions/tg-rotate-2026-10-10-0955.md` | 与请假规则一致：若 `should_skip_punch` 为真，应明确「今日跳 |
| 「当 」日 不同 今日 值班 值班各自规则不同 | `sessions/tg-rotate-2026-10-10-0955.md` | 周六、法定假、请假、值班各自规则不同；回答前必须用「当天」日历判定是报时刻还是说 |
| 「几 」时 不要 不要按平日默认时间猜 与调 先查 | `sessions/tg-rotate-2026-10-10-0955.md` | 私聊问「几点打卡」时，先查当日打卡日历与调度计划，再回答，不要按平日默认时间猜。 |
| ## 09 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-09-问表-专项负责人时先查工作簿与需求-owner-再答-来源留存表-dws-dws_source_.md` | 2026-10-09-问表-专项负责人时先查工作簿与需求-owner-再答-来源 |
| memory_open pinned tags 业务 业务分工事实 为准 | `sessions/tg-rotate-2026-10-09-1045.md` | 冷启动仍按 PINNED / MEMORY_OPEN / 按任务 tags 深读 |
| owner 于口 人类 优于 优于口头记忆 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | 负责人类问题：工作簿条目名 + 表名/需求文档里的 owner 字段，优于口头记 |
| 「来 」挂 与留 交叉 作簿 分析 | `sessions/tg-rotate-2026-10-09-1045.md` | 当日工作簿里「来源分析验证数据」挂在野花名下，可与留存表归属交叉印证。 |
| 人同 侧登 同样 在需 存表 样是 | `sessions/tg-rotate-2026-10-09-1045.md` | 该留存表在需求侧登记的负责人同样是**野花**。 |
| 0留 15留 30 30留） 7留 dws.dws_source_analysi | `sessions/tg-rotate-2026-10-09-1045.md` | 来源分析留存指标落在表 `dws.dws_source_analysis_ret |
| 业务 业务负责人是 为准 人是 以工 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | **来源留存**业务负责人是**野花**（需求/验证口径以工作簿为准）。 |
| memory 「来 」时 不凭 不凭印象或 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | 问「来源留存谁负责」时，先对工作簿和近期分工核对，不凭印象或 MEMORY 猜负 |
