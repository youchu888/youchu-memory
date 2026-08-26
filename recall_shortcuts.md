# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 08 2026 27 agent_session_rotate count | `~/.dc-platform/memory/lessons/2026-08-27-脏数据任务先-count-count-distinct-event_id-验重复-再导明细-配合.md` | 2026-08-27-脏数据任务先-count-count-distinct-e |
| ## 08 2026 27 agent_session_rotate cre | `~/.dc-platform/memory/lessons/2026-08-27-查-dwd_standard_dirty_data_df-前先对元数据-禁用臆测列-如无-cre.md` | 2026-08-27-查-dwd_standard_dirty_data_df- |
| 002 and app_id dt event event_id | `sessions/tg-rotate-2026-08-27-0651.md` | 过滤条件模板：`dt = '业务日' AND app_id = 'TSYH-00 |
| 4115 device dictvalues payload.type type | `sessions/tg-rotate-2026-08-27-0651.md` | 4115 条共性：全是 **`payload.type=device`**；拦因 |
| 002（ 4115 dt event_id tsyh user_register | `sessions/tg-rotate-2026-08-27-0651.md` | 本次 TSYH-002（`dt=当天`）`user_register`：**41 |
| $.payload.type as get_json_string payloa | `sessions/tg-rotate-2026-08-27-0651.md` | 排查注册脏数据时，用 `get_json_string(raw_data, '$ |
| app_id dt error_column error_info_list e | `sessions/tg-rotate-2026-08-27-0651.md` | 脏数据明细常用列：`dt, app_id, event, event_id, e |
| count csv distinct event_id 件自 先条数 | `sessions/tg-rotate-2026-08-27-0651.md` | 标准流程：**先条数**（`COUNT(*)` + `COUNT(DISTINC |
| create_time paimon paimon.dw.dwd_standar | `sessions/tg-rotate-2026-08-27-0651.md` | 查 **Paimon 脏表**（`paimon.dw.dwd_standard_ |
| create_time dirty_data dwd_standard_dirt | `sessions/tg-rotate-2026-08-27-0651.md` | [LESSON: paimon,dirty_data,sql/查 `dwd_st |
| sql 「变 「在 」时 不要 不要只解释或重复「在查」 | `sessions/tg-rotate-2026-08-27-0651.md` | 第一遍 SQL 列名/事件名写错时，**立刻改 SQL 重查并交付**，不要只解 |
| register user_register 「注 「注册事件」在脏表里事件名是 | `sessions/tg-rotate-2026-08-27-0651.md` | 「注册事件」在脏表里事件名是 **`user_register`**，不要未经核 |
| ## 08 2026 26 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-26-用户确认-传好了是吧-类追问时只复报日期-云端-id-状态-勿重复执行-upload-脚本.md` | 2026-08-26-用户确认-传好了是吧-类追问时只复报日期-云端-id-状态 |
| bus 不写 与内 专项 专项复盘 业务 | `sessions/tg-rotate-2026-08-26-0620.md` | 日报写作仍遵守：【今日结果】约 3 条、业务话展开、【死锁阻碍】【专项复盘】默认 |
| 08 1（ 27） op p1 to | `sessions/tg-rotate-2026-08-26-0620.md` | 续做 TOP1（截止 08-27）：按 v0.3 定稿推进建表、元数据与联调落地 |
| 08 2026 25 er v0.3 一期 | `sessions/tg-rotate-2026-08-26-0620.md` | 2026-08-25 指标库 v0.3 当日交付：ER 图定稿（指标/维度/实体 |
| 一致 与主 主人 云端 人给 仍按 | `sessions/tg-rotate-2026-08-26-0620.md` | 若本地已有同日定稿，仍按用户新贴正文覆盖后再传，保证云端与主人给定稿一致。 |
| id 「传 」时 一句 一句肯定 上传 | `sessions/tg-rotate-2026-08-26-0620.md` | 用户追问「传好了是吧」时，一句肯定 + 复报日期/ID/状态即可，不必重复跑上传 |
| id inserted 三项 上传 上传成功回执至少带三项 与留 | `sessions/tg-rotate-2026-08-26-0620.md` | 上传成功回执至少带三项：日期、云端记录 ID、状态（`inserted` 新建  |
| .cursor date dd dd.md log mm | `sessions/tg-rotate-2026-08-26-0620.md` | 本地定稿固定路径：`.cursor/work-log/reports/日报-YY |
| daily id lesson report up upload | `sessions/tg-rotate-2026-08-26-0620.md` | [LESSON: daily-report/用户确认「传好了是吧」类追问时只复报 |
| 「按 」时 一准 上传 个上 为唯 | `sessions/tg-rotate-2026-08-26-0620.md` | 用户说「按照这个上传云端」时，以粘贴的日报正文为唯一准绳：先落本地定稿，再上传， |
| ## 08 2026 25 60 ack | `~/.dc-platform/memory/lessons/2026-08-25-收到-mode-work-派单-60-秒内-ack-完工-reply-结案-审稿类任务按回执缺口.md` | 2026-08-25-收到-mode-work-派单-60-秒内-ack-完工- |
| ## 08 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-25-补设计可视化前先拉平台现网正文作-merge-底稿-避免本地补丁被后续版本覆盖后再审仍报缺.md` | 2026-08-25-补设计可视化前先拉平台现网正文作-merge-底稿-避免本 |
| ## 08 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-25-tg-重推日报前先确认推送脚本已改为只发正文无标题头-推完请主人在私聊目视验收.md` | 2026-08-25-tg-重推日报前先确认推送脚本已改为只发正文无标题头-推完 |
| id reply 一审 上传 下一 了哪 | `sessions/tg-rotate-2026-08-25-2018.md` | 覆盖上传开发平台可视化后：reply 里写清改了哪些 §、平台路径/id，并提示 |
| 1– c1 c4 dim_uses g7 published | `sessions/tg-rotate-2026-08-25-2018.md` | 「组合约束」类增补（C1–C4：dim_uses 成对、G7-b 三角等式、pu |
| er metric_standard §1 §12.5 §13.3 §15 | `sessions/tg-rotate-2026-08-25-2018.md` | 审稿常见缺口清单（本轮）：§1 九数基线、§12.5 事件字典自增长、§13.3 |
| git） memory youchu 一台 仍用 任务 | `sessions/tg-rotate-2026-08-25-2018.md` | 推送脚本/日报相关改动要同步进 `youchu-memory`（memory g |
| post_dail post_daily_report_to_dm.py tg  | `sessions/tg-rotate-2026-08-25-2018.md` | TG 日报私聊推送默认**只发正文**：去掉「📋 又初 · 日报 …（定稿自动推 |
| merge 「组 」版 不是 为底 以现 | `sessions/tg-rotate-2026-08-25-2018.md` | 再审/补稿前**必须先对平台现网正文**（本地稿 ≠ 现网）；若现网已是较新的「 |
| #f4f5f7 cdn er hi html mermaid | `sessions/tg-rotate-2026-08-25-2018.md` | 可视化 HTML 铁律：纯 HTML/SVG 手工 ER，禁 mermaid C |
| 0–4+2.5） 1– 66） 67 g1 g7 | `sessions/tg-rotate-2026-08-25-2018.md` | 设计可视化审稿（如 metric_library v0.3 id=66）：对照源 |
| 60 ack agent bus cursor reply | `sessions/tg-rotate-2026-08-25-2018.md` | agent-bus 派单：60 秒内先 `ack`，干完再 `reply` 结案 |
| date dd dd.md mm post_da post_daily_repo | `sessions/tg-rotate-2026-08-25-2018.md` | 主人说「重新推送昨天日报」时：先定位 `reports/日报-YYYY-MM-D |
| ho hot（须同时看「按时间最近动过」） ot t（ 「按 」） | `sessions/tg-rotate-2026-08-25-0616.md` | > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」 |
| ## 08 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-25-指标库-er-推文档库后须同步落仓-docs-metric_library_er_diagram.md` | 2026-08-25-指标库-er-推文档库后须同步落仓-docs-metric |
| ## 08 2026 25 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-08-25-会话-resume-失败续做时-先查本地稿并对齐最新-spec-表名再推文档库-勿用旧临时名或旧.md` | 2026-08-25-会话-resume-失败续做时-先查本地稿并对齐最新-sp |
| #410 #411 er 一任 不必 不必让用户重述需求 | `sessions/tg-rotate-2026-08-25-0616.md` | 私聊 #410/#411 的指标库 ER 任务，因前序会话失败未交；恢复会话后同 |
| docs git metric_library_er_diagram.md me | `sessions/tg-rotate-2026-08-25-0616.md` | 交付文档库后，仓库内同步留镜像：**`docs/metric_library_e |
