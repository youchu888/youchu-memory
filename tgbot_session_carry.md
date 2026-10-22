# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-22 · 最新归档：`sessions/tg-rotate-2026-10-22-1608.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 时间列禁止对 srViews 再减 8h**（`bus#10793` 曾因此退回）；推前必须自核 CAST/时区处理。
- [LESSON: agent-bus|狂人声明「我直接做、不要再推」→ 停改停推、reply 说明已推 commit 与是否需回滚，勿继续跟该线 JDBC/SR 草稿。]
- 渠道维表日快照（`dim_channel_info_all_snap`）取数源会随拍板切换：曾定业务库 bmp `system_channel_info` JDBC 日全量；后改 **prod SR `dim.dim_channel_info_all` 定时全量拉 → Paimon 按 `snap_dt` 留历史**。
- prod 有 **SR 只读账号**（查数/对账），与「快照 ETL 用哪条链路当源」是两件事；不能因「有 SR 只读」就默认快照一定读 SR，要以当前 bus/主人方案为准。
- 当时反对「只读 SR 当源」的两点仍作风险备忘：prod SR 该表曾 **长期 0 行**（后台只写 test SR）；且 SR 侧若仅 **新渠道 INSERT、无 UPDATE**，快照里渠道属性可能 **不是业务全量最新态**。
- 狂人 #11161 选 **A**：去掉 JDBC 依赖、不再催运维开业务库只读；源 `srViews` → SR 全量读，目标 `paimon.dim.dim_channel_info_all_snap`，**每天分区一份全量**。
- 调度：**05 槽**（与 `dim_app_info_all` 同槽），业务后台约 **01:30 写 SR 之后**再拉；挂槽/建 Paimon 表由狂人侧做。
- **时间列禁止对 srViews 再减 8h**（`bus#10793` 曾因此退回）；推前必须自核 CAST/时区处理。
- #11164 更正：**快照链路狂人直接做**（对齐归因配置的 **SR→Paimon 同步任务**）；SR 怎么写不归数仓讨论；又初侧 **停改、停推 JDBC 版**，已推 commit 是否回滚由狂人定。
- 方案摇摆时：先 **bus 对齐 A/B/C**，再改 SQL/文档/pipeline-runner；中途被「别人接手」要 **立刻停手** 并在 reply 里说明远端已有提交性质（如 `230fa1fb` 为 SR 草稿非 JDBC）。
- agent-bus：`mode=work` 须 **60s 内 ACK**，干完 **reply 列实活** 再结案；主人 oral 定调与 bus 拍板冲突时 **以最新 bus 为准**。
- 「上传云端」是独立触发词：与写日报、推 TG 分开，主人明确说后才跑上传，不要定稿后自动上传。
- 上传前必须先确认定稿文件存在（如 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 或 memory 镜像路径），再执行脚本。
- 上传内容必须与定稿 Markdown **原封不动**，禁止在上传前改字或二次润色。
- （本段无新坑；未追加 `[LESSON: …]`。）
- 未指定日期时，默认用当日 Asia/Shanghai 的 `YYYY-MM-DD` 作为 `--date`。
- 标准命令：`python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`（凭证走本机 `~/Downloads/工作报告/config.js`，不进 Git、不写进记忆）。
- 成功回执应带三要素：文件名、云端记录 ID、操作类型（如 `inserted` / 覆盖更新），便于主人核对。

