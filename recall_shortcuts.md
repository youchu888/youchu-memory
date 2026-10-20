# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 10 20 2026 agent_session_rotate co | `~/.dc-platform/memory/lessons/2026-10-20-commit-多任务并行-stash-冲突时先剥离无关-wip-再提交-避免-dim-同步-co.md` | 2026-10-20-commit-多任务并行-stash-冲突时先剥离无关-w |
| ## 10 20 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-20-dim-prod-sr-维表-0-行时-paimon-空-snap_dt-分区先判源表是否真无数.md` | 2026-10-20-dim-prod-sr-维表-0-行时-paimon-空- |
| ## 10 20 2026 844c4baf agent_session_rot | `~/.dc-platform/memory/lessons/2026-10-20-dim-paimon-sr-维表无-dt-列时禁止抄-dim_app_info_all-的-dt.md` | 2026-10-20-dim-paimon-sr-维表无-dt-列时禁止抄-di |
| commit dd5738d4 dim push sr→paimon 交付 | `sessions/tg-rotate-2026-10-20-1708.md` | 用户明确要求再 **commit/push**；交付 commit 例 **`d |
| 20 etl prod sr test 例行 | `sessions/tg-rotate-2026-10-20-1708.md` | test SR 有样例行（如约 20 行）可验逻辑；**prod SR 当前 0 |
| paimon session test 人） 切分 又初 | `sessions/tg-rotate-2026-10-20-1708.md` | **职责切分**：又初 = session + 同步稿 + test 可对账材料 |
| 001 20261020 dbprogramming dev session s | `sessions/tg-rotate-2026-10-20-1708.md` | 新链路 **`dbprogramming` 须建 dev session**（例 |
| ar dt in jo k（ oi | `sessions/tg-rotate-2026-10-20-1708.md` | 下游 Spark（渠道周/月/部门等）JOIN 维表时统一 **`WHERE s |
| creat created_at paimon sql sr sr_dim_ch | `sessions/tg-rotate-2026-10-20-1708.md` | 同步 SQL 结构：**`timer` + `srViews`**（如 `sr_ |
| 00 create ddl etl full_chain insert | `sessions/tg-rotate-2026-10-20-1708.md` | **ETL 只做 `INSERT OVERWRITE` 当天分区**，不在 ET |
| 844c4baf bus#10789 commit dim_channel_in | `sessions/tg-rotate-2026-10-20-1708.md` | 样板链：bus#10789 / commit **`844c4baf`**（测试 |
| dim.dim_channel_info_all dim_chann dim_c | `sessions/tg-rotate-2026-10-20-1708.md` | `dim.dim_channel_info_all` 无 `dt`，Paimon |
| by dim_app_info_all dt paimon partitione | `sessions/tg-rotate-2026-10-20-1708.md` | SR 维表同步 Paimon 先分两类：源表**自带按日 `dt` 全量**→照 |
| datacheck dim lesson paimon prod snap_dt | `sessions/tg-rotate-2026-10-20-1708.md` | [LESSON: datacheck/dim/prod SR 维表 0 行时 P |
| 844c4baf dim dim_app_in dim_app_info_all | `sessions/tg-rotate-2026-10-20-1708.md` | [LESSON: spark_migrate/dim/paimon/SR 维表无 |
| ## 10 20 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-20-海豚待发布撤回后统一-spark-化重走七步-被新版本覆盖或已有-spark-续作的-sessi.md` | 2026-10-20-海豚待发布撤回后统一-spark-化重走七步-被新版本覆盖 |
| ## 10 20 2026 ads agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-20-视频-ads-日报改源优先-dwm-用户视频中间表-缺列先商量-未迁完-dwd-读明细任务前禁止.md` | 2026-10-20-视频-ads-日报改源优先-dwm-用户视频中间表-缺列先 |
| ## 10 20 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-20-表上新列但任务不写时-以海豚-live-insert-列清单为准判是否发版-并对照同批-task.md` | 2026-10-20-表上新列但任务不写时-以海豚-live-insert-列清 |
| 013 20261016 _a _日 ad ads_channel_metric | `sessions/tg-rotate-2026-10-20-1308.md` | **渠道日指标 P0**：`ads_channel_metrics_daily_ |
| 10 20 dwd dwd.dwd_video_event_h paimon.d | `sessions/tg-rotate-2026-10-20-1308.md` | **视频迁源（10-20 定）**：读 SR `dwd.dwd_video_ev |
| full mcp put session stage state | `sessions/tg-rotate-2026-10-20-1308.md` | **session MCP 写 stage 失败**：用开发平台 **`PUT  |
| origin prod publish request session stag | `sessions/tg-rotate-2026-10-20-1308.md` | **修复顺序**：origin 对齐本地 → **先发 test** → TAS |
| dept_id live month_start_dt paid_type 与数 | `sessions/tg-rotate-2026-10-20-1308.md` | **部门月 `paid_type`**：进主键 `(month_start_dt |
| dept_code dim_app_info_all insert join p | `sessions/tg-rotate-2026-10-20-1308.md` | **产品周 `paid_type`**：INSERT 需 `dept_code` |
| l（ paid_type ql sq sql（例 task | `sessions/tg-rotate-2026-10-20-1308.md` | **半发漏发**：同需求批次里可能只有部分 task 上新 SQL（例：部门周已 |
| ddl es etl live prod） sql | `sessions/tg-rotate-2026-10-20-1308.md` | **列有、任务不写**：先四路对照——表结构（test/prod）、仓库 SQL |
| ads dwd dwm lesson migration paimon | `sessions/tg-rotate-2026-10-20-1308.md` | [LESSON: video-migration,paimon,dwd/视频 A |
| 013 20261016 _a _日 ad ads_channel_metric | `sessions/tg-rotate-2026-10-20-1308.md` | 渠道日指标 P0**：`ads_channel_metrics_daily_d` |
| full mcp put session stage state | `sessions/tg-rotate-2026-10-20-1308.md` | session MCP 写 stage 失败**：用开发平台 **`PUT …/ |
| ddl es etl live prod） sql | `sessions/tg-rotate-2026-10-20-1308.md` | 列有、任务不写**：先四路对照——表结构（test/prod）、仓库 SQL/D |
| bootstrap daily memory_open repor report | `sessions/tg-rotate-2026-10-19-2208.md` | 冷启动仍先读 bootstrap / MEMORY_OPEN，按任务再查规则；上 |
| g） pr prepare_daily_report_sync sync tg  | `sessions/tg-rotate-2026-10-19-2208.md` | 日报生成链路（双机 sync → 写稿 → 推 TG）与上传云端是**两阶段** |
| id inserted） 不必 不必写入长期记忆索引 主人 于主 | `sessions/tg-rotate-2026-10-19-2208.md` | 成功回执应包含：**日期**、**记录 ID**、**接口状态**（如 inse |
| api config） token upload_work_report.py  | `sessions/tg-rotate-2026-10-19-2208.md` | 凭证与 API 走既有脚本（如 `upload_work_report.py`  |
| asia dd mm shanghai yyyy 定日 | `sessions/tg-rotate-2026-10-19-2208.md` | 未指定日期时默认用 **Asia/Shanghai 当日** `YYYY-MM- |
| tg 一版 上传 上传前宜对照私聊推送记录 不一致 与定 | `sessions/tg-rotate-2026-10-19-2208.md` | 若当日已推 TG，上传前宜对照私聊推送记录，确认与定稿同一版，避免双机/手改导致 |
| dd.md memory mm reports yyyy 一正 | `sessions/tg-rotate-2026-10-19-2208.md` | 上传前以本地定稿 `reports/日报-YYYY-MM-DD.md`（或 me |
| 「上 「生 」分 」时 上传 不重 | `sessions/tg-rotate-2026-10-19-2208.md` | 用户说「上传云端」时，与「生成日报」分离：只跑上传脚本，不重写、不重新汇总正文。 |
| id」 tg 「已 上传 不要 保持 | `sessions/tg-rotate-2026-10-19-2208.md` | 对话收尾保持简短：确认「已上传 + 日期 + 记录 ID」，**不要**再贴完整 |
| markdown 「顺 」后 上传 上传必须 不动 | `sessions/tg-rotate-2026-10-19-2208.md` | 上传必须**原封不动**提交 Markdown；禁止「顺手润色、补条、改格式」后 |
