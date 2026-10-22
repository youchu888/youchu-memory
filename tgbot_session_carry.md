# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-22 · 最新归档：`sessions/tg-rotate-2026-10-22-2209.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 对外回复（TG 私聊、Cursor 对话、推给你的正文）禁用「主人」，一律用「你」直说。
- 内部记忆、规则出处可保留「主人」等词；**写给用户的输出必须剥离**，口误后要按铁律重写而非只道歉。
- 定稿后**立刻** `post_daily_report_to_dm.py` 推 TG；对话里只确认「已推 + 定稿路径」，**不要贴全文**（避免与 TG 双份）。
- 「按这个上传云端」= 以**当前定稿原封不动**跑上传脚本；上传前禁止改字、禁止顺手润色。
- 上传成功可在回复中说明日期与记录状态（如 inserted）；**不要**在蒸馏/对外摘要里写 apiToken、完整 API 凭证或无关内部 ID 习惯化泄露（业务需要的 record id 一句即可）。
- [LESSON: 称呼|对外回复禁用「主人」，一律用「你」；内部可留出处词，输出必须剥离]
- 「重新生成日报」= 完整日报链路重做，不是局部改稿：先双机 `prepare_daily_report_sync`，再读金样与当日 work-log / transcript，后写稿。
- 旧草稿若含违规称呼或与当日实活不符，重生成时要**全文重写并核对实活**，再推 TG，不能仅替换一个词。
- 定稿路径：`.cursor/work-log/reports/日报-YYYY-MM-DD.md`（含 memory 镜像）；未说「上传云端」则不上传。
- 时间列禁止对 srViews 再减 8h**（`bus#10793` 曾因此退回）；推前必须自核 CAST/时区处理。
- [LESSON: agent-bus|狂人声明「我直接做、不要再推」→ 停改停推、reply 说明已推 commit 与是否需回滚，勿继续跟该线 JDBC/SR 草稿。]
- 渠道维表日快照（`dim_channel_info_all_snap`）取数源会随拍板切换：曾定业务库 bmp `system_channel_info` JDBC 日全量；后改 **prod SR `dim.dim_channel_info_all` 定时全量拉 → Paimon 按 `snap_dt` 留历史**。
- prod 有 **SR 只读账号**（查数/对账），与「快照 ETL 用哪条链路当源」是两件事；不能因「有 SR 只读」就默认快照一定读 SR，要以当前 bus/主人方案为准。
- 当时反对「只读 SR 当源」的两点仍作风险备忘：prod SR 该表曾 **长期 0 行**（后台只写 test SR）；且 SR 侧若仅 **新渠道 INSERT、无 UPDATE**，快照里渠道属性可能 **不是业务全量最新态**。
- 狂人 #11161 选 **A**：去掉 JDBC 依赖、不再催运维开业务库只读；源 `srViews` → SR 全量读，目标 `paimon.dim.dim_channel_info_all_snap`，**每天分区一份全量**。
- 调度：**05 槽**（与 `dim_app_info_all` 同槽），业务后台约 **01:30 写 SR 之后**再拉；挂槽/建 Paimon 表由狂人侧做。
- **时间列禁止对 srViews 再减 8h**（`bus#10793` 曾因此退回）；推前必须自核 CAST/时区处理。
- #11164 更正：**快照链路狂人直接做**（对齐归因配置的 **SR→Paimon 同步任务**）；SR 怎么写不归数仓讨论；又初侧 **停改、停推 JDBC 版**，已推 commit 是否回滚由狂人定。

