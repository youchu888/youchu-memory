# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-15 · 最新归档：`sessions/tg-rotate-2026-08-15-0632.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 用户贴**已定稿**日报正文并说「按这个上传云端」时，先落本地 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`，再跑上传脚本；**正文与用户所给一字不改**。
- 记忆冷启动包只作**索引入口**；按任务 tags 再深读 lesson，禁止整包灌入后假装已用过。
- 同一定稿若已上传成功（有 record ID），**不要重复跑上传**，避免重复操作或状态混淆。
- 「上传云端」与写日报、推 TG 是**分开指令**；本会话只做云端提交，不自动补写或改写条目。
- 上传成功可回执三要素：**日期**、**记录 ID**（如 72350）、**状态**（`inserted` 表示新建，同日同类型会覆盖）。
- 日报【今日结果】写**业务交付**，不写内部排查链；示例：大漏斗日表对接文档、停留时长口径说明、站群搜索词 TOP 与补数量级核对。
- 大漏斗日汇总表对接文档应含：**字段说明 + 建表语句**，方便后端按同一结构接数。
- 用户停留时长口径交付需一次性写清四块：**怎么算、末页怎么处理、只看一页怎么计、五档区间怎么划成四段**。
- 站群来源搜索词任务通常含两步：**当日 TOP 词条探查回传** + **历史明细补数已跑日期的量级核对**。
- 【明日动作】可从当日续做项推断；示例 TOP1 补数逐日核对（带截止日）、TOP2 指标库设计按评审意见修订。
- [LESSON: agent-execution|汇报任务进度前先查集群日志、outgoing 产物、bus 结案状态，禁止未核实就下「没干/没跑」结论]
- **大漏斗后端对接**：表 `dws.dws_app_event_funnel_d_d`；粒度 `(dt, app_id, is_new)`；4 维度列 + 18 事件 × 3 指标（`user_cnt`/`session_cnt`/`event_cnt`）= 54 列；口径字典见平台 `metric_big_funnel_event_dictionary`。
- **DDL 双份**：主跑 Paimon 在 `ops_system/04.dws/dws_app_event_funnel_d_d/spark/sql/…paimon.ddl.sql`；后端对接 SR 形态在同级 `dws_app_event_funnel_d_d_ddl.sql`；设计见 `spec.md`/`design.md`。
- **私聊要表结构时**：从仓库整理成「对接说明 md + 纯 DDL sql」两文件，放到 `omdb/tgbot/outgoing/` 再 `[SEND_FILE]`；不必纠结 Paimon/SR，表结构一致。
- **交付缺口常见形态**：口径/DDL 已在仓或平台，但未单独打包成「后端对接包」私聊发出；SR 同步未就绪时后端默认查 SR 可能接不上。
- **dwd_*_r 历史补数分工（#6488）**：狂人起作业（`chain_range_cached.sh`，08-09→07-13 倒序 28 天）；又初**只验数、不起作业**；异常 bus 狂人，不自行修。
- **补数验数节奏**：按 `_summary.tsv` + `verify_*.log` 逐日验 15 张表量级；与相邻日一致、无 0 行/数量级跳变即通过；A/B 已定缓存版（1652s vs 5410s）。
- **站群关键词探查**：脚本在 `ops_system/_probe/site_group_search_kw/`，上 hadoop-1 跑；结果日志在 `site_group_search_kw/logs/`；口径狂人 #6417 已交，跑完 TOP 词条 + 条数 bus 结案。

