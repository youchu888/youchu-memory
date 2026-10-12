# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-12 · 最新归档：`sessions/tg-rotate-2026-10-12-1756.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 新增、次留、日均活跃**仍按人去重/既有口径，**禁止**像金额一样按日简单加总。
- [LESSON: 渠道周月表,ads_channel_promotion|周月充值三列对 ads.ads_channel_promotion_summary_d 同期 SUM（VIP / 扣量 VIP / 金币）；新增与次留禁止按日相加]
- [LESSON: 渠道周月表,次留口径|次留 = 该渠道新增与次日全 App 活跃的交集，不要求回访仍在注册渠道；人数落在注册渠道行]
- 渠道推广周表 `ads.ads_channel_promotion_summary_w`、月表 `ads.ads_channel_promotion_summary_m` 最小粒度是**渠道**，不是部门；一行 = 自然周/月 × App × `channel`。
- 周表主键：`week_start_dt, app_id, channel`（分区键为周一 `week_start_dt`）；月表主键：`month_start_dt, app_id, channel`（分区键为月初 `month_start_dt`）。
- `dept_id` / `dept_name` 仅为渠道属性，**不进主键**；部门取自 `dim.dim_channel_info_all`（`app_id` + 渠道码），**不用**产品维表上的部门。
- 按部门看数：在渠道行上筛选或汇总，**不会**再拆出「部门 × 渠道」之外的更细行。
- 结算日汇总 `ads.ads_channel_promotion_settlement_summary_d` 只有点击 IP、注册等，**没有充值**；问「结算充值能不能拿」不能只看这张表。
- 充值明细在 `dws.dws_settlement_detail`（`order_paid`），已落到「日 × App × 渠道」的推广日/小时汇总；周月扩展应 **SUM 日表**，不必重扫结算明细。
- 日表三列金额（可跨天相加）：`recharge_amount`（VIP 订阅）、`deduction_recharge_amount`（扣量后 VIP）、`coin_recharge_amount`（金币）。
- 周月新增充值字段：`week_*` / `month_*` 与上三列一一对应；主键不变；**金额**在自然周/月内、截至 T-1 对 `ads.ads_channel_promotion_summary_d` **直接 SUM**。
- **新增、次留、日均活跃**仍按人去重/既有口径，**禁止**像金额一样按日简单加总。
- 渠道次留易错点：旧逻辑要求「次日活跃渠道 = 注册渠道」会漏换渠道回访用户；正确是**该渠道新增用户 ∩ 次日在该 App 任意渠道活跃**，人数仍记在**注册渠道**行。
- 改 SQL/DDL 后：test 表可先改完，**海豚未重发、任务未重跑**则历史分区充值仍为 0、次留仍为旧口径；验收要看发布+补跑后数据。
- 用户说「现在重新打卡 / 补打上班卡」时，先查当日打卡入口与计划窗口，再立刻执行补打，不要只复述失败原因。
- OneHR 上班卡成功以 HTTP 200 为准；回执里应写清北京时间、是否通过截图校验与上传。
- 09:50、09:52 等「接口断开」多为瞬时故障；只要在计划窗口内，调度重试仍可能成功（本例 09:56 打成）。
- 补打成功后顺带说明下班卡仍按原计划（如 19:16），避免用户误以为全天 schedule 被改乱。

