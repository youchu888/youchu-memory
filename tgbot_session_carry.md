# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-03 · 最新归档：`sessions/tg-rotate-2026-11-03-1201.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 临发布被拦**：先写清现状（session 阶段、源表/事件、目标表、是否影子/对平），**bus 狂人拍板**，勿自行改 `pb_*` 或硬提审。
- 须狂人定的四项**：是否必须先挂影子、影子/正式表名、当日能否发、是否立刻改 `pb_*`；回执后再改稿或继续 Stage7。
- [LESSON: dev-session|agent-bus|临发布] 野花指「不符合狂人规则」且当日要发：汇总口径与表结构 → bus 狂人 → 收到表名/影子/能否发后再动 SQL 或提审，禁止未拍板就改 pb 或 request-publish。]
- **页面点击率**链路：`dev-20261020-002`，Stage1–6 已完、Stage7 待审；产表**尚未建、未发过**，当日仍有机会改口径再首发。
- **取数**：直读 `dw.dw_user_event_detail_new`；事件 `app_pageitem_exposure` / `app_pageitem_click`，按**次数**汇总。
- **产出**：`ads.ads_page_item_ctr_d` + `dim.dim_app_page_item_d`（Paimon → SR）。
- **不合规高发点**：现稿**直写正式表**，无**影子表**、无**7 日对平**；对照当日「页面点击率也进影子闸」（如 bus#12151）即野花所指。
- **临发布被拦**：先写清现状（session 阶段、源表/事件、目标表、是否影子/对平），**bus 狂人拍板**，勿自行改 `pb_*` 或硬提审。
- **须狂人定的四项**：是否必须先挂影子、影子/正式表名、当日能否发、是否立刻改 `pb_*`；回执后再改稿或继续 Stage7。
- **对外沟通模板**：取数表 + 事件名 + 产出表 + 影子/7 日闸差距 + 发布急迫性，一条 bus 问规则符合性即可。
- 补齐流程：**对照健康 session → 真查 test（stage4）与 prod 缺口（stage5）→ 写回五件 → 挂 outputs / 海豚 target → 补全 playbook**；禁止只改 stage 状态。
- spark_migrate 与 05.ads 海豚稿分离**：周表 Spark 稿勿被海豚 SQL 覆盖；只对齐 **05.ads 海豚发布路径**。
- [LESSON: dev-session,stage7,rel_dir|提审前自检：五件齐、`rel_dir`/outputs/海豚 binding 齐、artifact 非空、本地 SQL 与 test 海豚一致；缺任一项先补再 RP，勿空标 done。]
- dev session 列表能 **pending**，但 stage7 审发布打不开，常见原因是 **stage 1～6 标了 done 却缺 `state_json` 五件**（`strict_mode`、`owner_boundary`、`stage4_db_check`、`stage5_prod_dryrun`、`stage6_commit`），不是单纯「没提审」。
- 五件缺任一项，审核插件读不到真查库 / dryrun / commit 证据，**审发布界面会挂**；仅有 `stage6_commit` 仍不够。
- **`rel_dir` 为空或 `outputs=[]`** 时，插件无法在本机对上目录，**连打开都困难**；本地已有 `ops_system/...` 也要在平台上挂好路径与 outputs。
- 平台 artifact 里 **playbook/README 空壳**、海豚 **`wf_code`/`project_code` 空**，和 state 缺件叠加时，即使有 `rel_dir` 也 **审不了**。
- 提审前 **本地 SQL 须与 test 海豚线上一致**（如推广窗 `promote_start/end`）；发现 test 已改、git 未跟时，**先对齐再 RP**。

