# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-08 · 最新归档：`sessions/tg-rotate-2026-11-08-0600.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- TG 超大 prompt**：不必通读全文；读**开头指令 + 末尾「当前问题」**，按末尾问题直接执行，勿复述文件。
- agent-bus `mode=work`**：60 秒内 `ack`，干完再 `reply` 结案；**reply 成功前不要 mark 结案**；同一 Cursor 主会话处理，勿 spawn 新 Agent。
- 下游挂账口径（狂人口径）**：入湖未恢复时 **27 条挂账不动、不补不弃**；`pb_dws_app_user_d_h_hourly` 等挂的是**当日业务小时格**（如 11-08 的 03#04），不是错绑到 11-07；**等入湖探针放行后任务自续跑**，勿乱补历史格。
- [LESSON: paimon|SR-normal-Paimon-stuck|先比 Paimon 表最晚 etl_time 与 SR 结算等同窗水位；SR 在写、Paimon 不动则升级 Fanout/Flink（@斯科特），勿在下游盲补]
- [LESSON: agent-bus|P0-lake|ACK 后只做只读复现 + 业务小时漏量核对 + 升级回执；挂账任务按「探针放行自续」处理，禁止入湖未恢复时批量补弃]
- [LESSON: daily-report|upload|上传前锁定定稿文件，禁止改字；仅主人要求「上传云端」时跑脚本，成功回 code 与稿路径]
- **日报上传云端**：先确认当日定稿路径（如 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`），**正文原封不动**再跑 `upload_work_report.py`；成功以 API `code=0` 为准，对话里报 `id` 与稿路径即可。
- **TG 超大 prompt**：不必通读全文；读**开头指令 + 末尾「当前问题」**，按末尾问题直接执行，勿复述文件。
- **agent-bus `mode=work`**：60 秒内 `ack`，干完再 `reply` 结案；**reply 成功前不要 mark 结案**；同一 Cursor 主会话处理，勿 spawn 新 Agent。
- **入湖停写判责**：对比 **Paimon**（注册 `dwd_user_register_d_v2_r` / 订单 `dwd_order_paid_d_r` 最晚 `etl_time`）与 **SR**（如 `dws_settlement_detail` 仍持续推进）；事件流/SR 正常而 Paimon 长时间无新批 → 瓶颈在 **Fanout/Flink 入湖**，不是下游 ETL 单点。
- **无 Fanout 权限**：不擅自动 Fanout/Flink；**群里 @斯科特（scott_188）** P0 升级，回执写清复现水位、SR 对照、msg id。
- **P0 复测**：二次停写时记录「只出一批又停」、距最晚 `etl` 的无提交时长、按业务小时漏量（如 03 点注册量级异常低），与首次告警一并 escalation。
- **下游挂账口径（狂人口径）**：入湖未恢复时 **27 条挂账不动、不补不弃**；`pb_dws_app_user_d_h_hourly` 等挂的是**当日业务小时格**（如 11-08 的 03#04），不是错绑到 11-07；**等入湖探针放行后任务自续跑**，勿乱补历史格。
- **停写前兆**：若停前已长期高延迟（数十分钟～数小时），告警里应同时写「停写时刻 + 停前延迟」，便于排障区分「新故障」与「恶化断流」。
- **结案回执要素**：Paimon 最晚 `etl_time`、SR 最新写入时刻、是否已 @ 升级、bus reply id；runner/渠道小时表等**追平与补数**按派单人计划，己侧无权限的不承诺自修 Fanout。
- 溯源结论要落到**责任边界**：`dw` 是镜像，镜中无该事件时先找源头补事件，而不是先找 `dw` 表维护人。
- 私聊「上传云端」须以**已定稿 Markdown 原样**跑上传脚本，上传前**不得改写**正文。
- 日报定稿路径与 API 回执（如 inserted id）可记一句便于核对，**勿在记忆蒸馏中保留 token/密钥**。

