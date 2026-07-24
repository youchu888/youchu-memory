# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-24 · 最新归档：`sessions/tg-rotate-2026-07-24-2111.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 用户日增量表**：`dim.dim_user_daily_snapshot`（替代已停 SCD2 拉链 `dim_user_zipper`）；session `dev-20260713-002`；PK `(dt, app_id, uid)`，23 列；勿与 `dws_user_finance_d`（金额专项）混淆。
- 归因回写顺序**：`dim_user_all` 构建 → `result_d` 计算 → `channel_apply` 回写 → 下游读 `dim.channel`；禁止单独重跑 result，补数须 **result → apply 级联**。
- 查岗未回根因**：进程未断，旧 handler 条件过严（固定 marker + 固定题干格式）且未命中时**静默 return 无日志**；Telethon 链路正常。
- 运维小坑**：TG 群发 urllib 易超时，改 curl；主人说「不要在群里回复」时只私聊/查日志；SELECT 模拟 UPDATE 可先行验 prod 待回写行再提交。
- [LESSON: attendance,tgbot|查岗 handler 未命中须打 debug 日志，触发条件收成「抽查群 @ 即尝试解析」，勿依赖固定 marker 字符串]
- [LESSON: attribution,dim|归因 apply 须同步回写 `dim_user_daily_snapshot` T-1 分区 channel，与 all 表同口径；禁止单独重跑 result]
- **TG 绿点保活**：`com.youchu.tg-work-online` 仅工作日 **09:30–22:30** 自动在线；周日/法定假/请假日不连；用户不必开 TG，每 45s ping 一次；22:30 自动下线变灰；与 `tgbot-daemon` 独立。
- **绿点配置入口**：`.env` 的 `TG_WORK_ONLINE_START/END`；`TG_WORK_ONLINE_ENABLED=false` 可关；请假跑 `set_leave_day.py` 当天跳过连线。
- **用户日增量表**：`dim.dim_user_daily_snapshot`（替代已停 SCD2 拉链 `dim_user_zipper`）；session `dev-20260713-002`；PK `(dt, app_id, uid)`，23 列；勿与 `dws_user_finance_d`（金额专项）混淆。
- **快照调度**：早窗 `wf_用户日快照_日` @00:15（early）+ 全量挂 `wf_dim_维度_日` @04:50（full）；宇宙四源 pv/login/register/order_paid，当日有任一动作才入表。
- **归因回写顺序**：`dim_user_all` 构建 → `result_d` 计算 → `channel_apply` 回写 → 下游读 `dim.channel`；禁止单独重跑 result，补数须 **result → apply 级联**。
- **回写开关与条件**：`is_run=1` 才算归因；`is_rewrite_channel=1` 才真写 dim；success + 渠道非 organic + dim 当前 organic/空才覆盖；**不动** `register_channel`；已有真实非 organic 渠道不覆盖。
- **快照 channel 回写（新增）**：apply 任务 Step2 同步 UPDATE `dim_user_daily_snapshot` **仅 dt=T-1**；规则与 all 表对齐；S1b 不碰已有行 channel；`rewrite_status` 仍以 all 表为准。
- **归因失败诊断（HTML）**：YD 系无数据→查 app 上线与 `user_register` 上报；多数 JHG→`is_run` 未配 + 客户端 `attribution_flag:0`；JHG-004 已开但落地页候选缺失、打分&lt;40、`device_brand/model` 全空。
- **查岗未回根因**：进程未断，旧 handler 条件过严（固定 marker + 固定题干格式）且未命中时**静默 return 无日志**；Telethon 链路正常。
- 设备标签 #5.2 进度同步应分三块：**已完成**（验数结论+补数区间+行数+指标 sanity）、**卡点**（待拍板/环境阻塞）、**下一步**（stage/依赖项），便于群聊一眼扫清
- SF-81 Paimon 试点验数 PASS 后，宽表 `calc_dt=07-20` 约 11.1 万行；核查重点看 **avg7/15/30 未塌缩**、**lifecycle 分布正常**
- TG/群消息发送若 **urllib 超时**，kill 后改 **curl** 重发；勿让 hung 请求占着

