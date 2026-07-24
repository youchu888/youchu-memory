# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-25 · 最新归档：`sessions/tg-rotate-2026-07-25-0601.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 群聊问进度：**第一句给结论**（如「还在对齐、两边都还没首跑」），再补 2~4 条 `·` 列点，别铺表格和 `##`
- 回群进度前**先核对 bus 实际进展**（如 bus#5471 / checkpoint 回执），勿凭记忆或草稿状态报
- 验数/派活若 bus 写明「结论请回 bus」→ **验完直接 agent-bus reply 结案**，群里 @ 提问者一句带过即可
- 群聊你是 **初儿**（`@youchu_ai_bot`）；**禁止**让同事 `@又初`；结尾固定「有疑问 @worker_ant_bot 或 @youchu_ai_bot」
- [LESSON: paimon-shadow|影子压测用独立 Spark wf + `_shadow` 表，源侧对齐后再首跑，严禁动现网 SR]
- [LESSON: tg-group|群聊进度第一句给结论，回前核对 bus 实态，列点 ≤4 条用 `·`，验完 bus 结案再群里一句带过]
- Paimon 影子压测双线：`A`=`paimon.dim.dim_user_daily_snapshot_shadow` + `wf_paimon_用户日快照_压测`；`B`=`paimon.dws.dws_register_attribution_result_d_shadow` 独立 wf
- Shadow 压测走 Spark 另起链路，**不动现网 SR**；表名带 `_shadow`，wf 独立命名便于对拍
- `B` 线归因 shadow 源读 Paimon 的 register + landing click/view；开跑前先探 **landing 分区映射**，探完再 bus 回协作方
- 双线分工后进度口径：各报 **wf 名 + 预计开跑时间**；首跑后互 ping **耗时 / 行数**
- 卡点要写清：**谁在等什么**（A 等 Spark 骨架；B 等 landing 分区映射）+ **下一步动作**（探完 bus 回野花）
- 群聊列点**最多 4 条**；私聊可长，群里让人扫一眼就懂
- 群聊**别暴露内心戏**（「我先对 inbox」「这条没 @ 我不回」等）；没 @ 的活直接不回，也别在回复里解释
- 用户日增量表**：`dim.dim_user_daily_snapshot`（替代已停 SCD2 拉链 `dim_user_zipper`）；session `dev-20260713-002`；PK `(dt, app_id, uid)`，23 列；勿与 `dws_user_finance_d`（金额专项）混淆。
- 归因回写顺序**：`dim_user_all` 构建 → `result_d` 计算 → `channel_apply` 回写 → 下游读 `dim.channel`；禁止单独重跑 result，补数须 **result → apply 级联**。
- 查岗未回根因**：进程未断，旧 handler 条件过严（固定 marker + 固定题干格式）且未命中时**静默 return 无日志**；Telethon 链路正常。
- 运维小坑**：TG 群发 urllib 易超时，改 curl；主人说「不要在群里回复」时只私聊/查日志；SELECT 模拟 UPDATE 可先行验 prod 待回写行再提交。
- [LESSON: attendance,tgbot|查岗 handler 未命中须打 debug 日志，触发条件收成「抽查群 @ 即尝试解析」，勿依赖固定 marker 字符串]

