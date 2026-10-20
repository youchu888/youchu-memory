# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-20 · 最新归档：`sessions/tg-rotate-2026-10-20-1308.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 列有、任务不写**：先四路对照——表结构（test/prod）、仓库 SQL/DDL、海豚 live SQL、同批相邻 task；常见根因是 **DDL 已落、含新列 ETL 未发 live**，不是「仓库没写」。
- session MCP 写 stage 失败**：用开发平台 **`PUT …/full` 合并 state** 再提审，勿空标 stage。
- 渠道日指标 P0**：`ads_channel_metrics_daily_d`（`wf_ads_日报表_日` / `dev-20261016-013`）提前；视频段从 dwd 改为读 behavior 宽表，影子验证 PASS 再切。
- [LESSON: video-migration,paimon,dwd|视频 ADS/日报改源优先 dwm 用户视频中间表，缺列先商量；未迁完 dwd 读明细任务前禁止停拆事件慢 task。]
- **列有、任务不写**：先四路对照——表结构（test/prod）、仓库 SQL/DDL、海豚 live SQL、同批相邻 task；常见根因是 **DDL 已落、含新列 ETL 未发 live**，不是「仓库没写」。
- **半发漏发**：同需求批次里可能只有部分 task 上新 SQL（例：部门周已写 `paid_type`，产品周/部门月仍旧版）；不能因「有一张已发」推断整批已对齐。
- **产品周 `paid_type`**：INSERT 需 `dept_code` + `paid_type`，JOIN `dim_app_info_all`；验数看 0/1/2 与维表未命中 `-1` 分布是否合理。
- **部门月 `paid_type`**：进主键 `(month_start_dt, dept_id, paid_type)`，粒度改为按免费/付费拆行；live 仍是旧粒度时主键与数据都会错。
- **修复顺序**：origin 对齐本地 → **先发 test** → TASK_ONLY 补数验列 → stage4 产物写 session → **request-publish 产**；无 prod 直发权时 prod 等审过再补数。
- **session MCP 写 stage 失败**：用开发平台 **`PUT …/full` 合并 state** 再提审，勿空标 stage。
- **视频迁源（10-20 定）**：读 SR `dwd.dwd_video_event_h` 的海豚任务要先迁，迁完才能停「拆视频事件」两个慢 task；指标尽量读 **`paimon.dwm.dwm_user_video_behavior_d`**（用户×天，`view_cnt` 等）和 **`paimon.dwm.dwm_user_video_d_d`**，禁止为省事回扫 dwd；中间表缺列先对齐再改，不私自绕回 dwd。
- **渠道日指标 P0**：`ads_channel_metrics_daily_d`（`wf_ads_日报表_日` / `dev-20261016-013`）提前；视频段从 dwd 改为读 behavior 宽表，影子验证 PASS 再切。
- **海豚待发布全撤（10-20）**：名下被撤 session **改 Spark 版、重走开发平台七步，不再上海豚**；过时不单做：`904` 已被 V1.0.11 覆盖，`60624-001` 续现有看板 Spark `016-006`。
- **Spark 待做清单（推广+归因+会话）**：推广三张（渠道周/部门月续 `015`/`018`，产品周新建）→ 归因 result 新建 → sid 宽表 → 使用时长五档；与渠道日 P0 排期对齐。
- 上传必须**原封不动**提交 Markdown；禁止「顺手润色、补条、改格式」后再传。
- 对话收尾保持简短：确认「已上传 + 日期 + 记录 ID」，**不要**再贴完整日报正文（防与 TG 双份）。
- 用户说「上传云端」时，与「生成日报」分离：只跑上传脚本，不重写、不重新汇总正文。
- 上传前以本地定稿 `reports/日报-YYYY-MM-DD.md`（或 memory 镜像路径）为唯一正文来源。

