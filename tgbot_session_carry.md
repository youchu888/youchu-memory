# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-25 · 最新归档：`sessions/tg-rotate-2026-08-25-0616.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 指标库 ER 图必须以用户指定的 **`spec_v0.3_20260824.md`** 为准；v0.3 扩层表名用正式稿 **`entity_dict` / `event_ext` / `role_dict`**，不用旧的 `domain_entity` 等临时名。
- 用户问「画好了吗 / 推文档库」时，标准链路：**核对 spec 版本 → 对齐表名重画 → 推文档库 → 报 slug/链接 → 附本地镜像路径**；未明确要求不要擅自 commit/push。
- 「正常了可以干活吗」类探活：短答可干活 + 点明根因（会话连不上）+ 列出可续两项（ER 图 / 其它数据活），让用户直接指定下一步。
- [LESSON: cursor-session,metric-library,er-diagram|会话 resume 失败续做时，先查本地稿并对齐最新 spec 表名再推文档库，勿用旧临时名或旧版 spec 交差]
- Cursor 会话 `resume` 被丢弃时，故障在 IDE 连接/会话恢复，不等于业务逻辑或数据本身出错；恢复后先说明原因再续做。
- 会话中断后续做，先查本地是否已有半成品（如 `docs/metric_library_er_diagram*.html/.md`），再对照用户最新 spec 决定补全还是重画，避免盲重做或交旧稿。
- 配色约定：蓝 = v0.2 指标核（concept / label / implementation / candidate）；黄 = v0.3 扩层；绿 = `report_metric_binding` 报表闭环；灰 = glossary / 表列挂接。
- 文档库推送指标库 ER：分类 **指标库**；slug 建议带版本与日期，如 **`metric_library_er_diagram_v03_20260824`**（示例 id=65）。
- 交付文档库后，仓库内同步留镜像：**`docs/metric_library_er_diagram_20260824.html`** + **`docs/metric_library_er_diagram.md`**，便于 Git 追溯与二次修改。
- 私聊 #410/#411 的指标库 ER 任务，因前序会话失败未交；恢复会话后同一任务可无缝续做，不必让用户重述需求。
- 此类错误与**模型额度用尽**、`unavailable for your plan` 等 quota 问题要分开看，勿混为一排查
- 用户问「为什么一直失败」时，多半是同一会话反复 hit 失效 resume；Bot 已自愈清 resume，**不需要再查业务根因**
- （已有 lesson「传输故障 vs 业务逻辑」「轮换前先沉淀」，本条无新增铁律，不硬写 LESSON。）
- TG 私聊报「Cursor 会话连接失败」属于**传输/会话层**故障，不是业务 SQL、ETL 或派单逻辑错
- Bot 检测到 `failed to connect/resume`、`session expired/invalid` 等模式时，会**自动丢弃失效的 `cursor_chat_id`（旧 resume）**，避免下一条继续 `--resume` 卡死
- 用户侧标准恢复：**原句重发**即可（resume 已清，下一条会新开 Cursor 会话）；或发 **「重启 agent」** 强制轮换
- 「重启 agent」会走 `rotate_workspace_session`：杀僵 agent、清 in_progress、强制新开共用会话，并 TG 通知

