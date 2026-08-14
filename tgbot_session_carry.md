# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-14 · 最新归档：`sessions/tg-rotate-2026-08-14-1532.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- [LESSON: agent-execution|汇报任务进度前先查集群日志、outgoing 产物、bus 结案状态，禁止未核实就下「没干/没跑」结论]
- **大漏斗后端对接**：表 `dws.dws_app_event_funnel_d_d`；粒度 `(dt, app_id, is_new)`；4 维度列 + 18 事件 × 3 指标（`user_cnt`/`session_cnt`/`event_cnt`）= 54 列；口径字典见平台 `metric_big_funnel_event_dictionary`。
- **DDL 双份**：主跑 Paimon 在 `ops_system/04.dws/dws_app_event_funnel_d_d/spark/sql/…paimon.ddl.sql`；后端对接 SR 形态在同级 `dws_app_event_funnel_d_d_ddl.sql`；设计见 `spec.md`/`design.md`。
- **私聊要表结构时**：从仓库整理成「对接说明 md + 纯 DDL sql」两文件，放到 `omdb/tgbot/outgoing/` 再 `[SEND_FILE]`；不必纠结 Paimon/SR，表结构一致。
- **交付缺口常见形态**：口径/DDL 已在仓或平台，但未单独打包成「后端对接包」私聊发出；SR 同步未就绪时后端默认查 SR 可能接不上。
- **dwd_*_r 历史补数分工（#6488）**：狂人起作业（`chain_range_cached.sh`，08-09→07-13 倒序 28 天）；又初**只验数、不起作业**；异常 bus 狂人，不自行修。
- **补数验数节奏**：按 `_summary.tsv` + `verify_*.log` 逐日验 15 张表量级；与相邻日一致、无 0 行/数量级跳变即通过；A/B 已定缓存版（1652s vs 5410s）。
- **站群关键词探查**：脚本在 `ops_system/_probe/site_group_search_kw/`，上 hadoop-1 跑；结果日志在 `site_group_search_kw/logs/`；口径狂人 #6417 已交，跑完 TOP 词条 + 条数 bus 结案。
- **被问「昨晚活干没干」**：分条对照派单——已闭环 / 进行中 / 确实欠着；欠着要认，不混在已做项里。
- **inbox 误标未结案**：bus 早回过但 inbox 仍 open 会反复被催（如停留四段口径 #4342→#6485）；reply 成功才算结案。
- **汇报前必查现场**：探查类任务先查集群日志、bus 结案记录，再答「跑没跑」；未核实就答「没跑」会误报欠账。
- **优先级陷阱**：补数盯盘、bus 回执、口径交底占满注意力时，知秋点名的一次性探查（不需等人）仍须排期闭环，不能无限后搁。
- **主人要求（#313）**：安排的活都要干——**可以延迟，不能不做**；无指令也可自主判断该推进什么，先干再报，灵活主动。
- [LESSON: daily-report|写明日动作前先对当天周几，周四及以后禁写「周中」作截止，改「周五」等具体日期]
- [LESSON: agent-bus|Spark/YARN 补数或 A/B 判定跑完后须立刻 bus reply 报秒数与选型，勿等催办才回执]
- `AGENT_LOOP_WAKE_DAILY_REPORT` 21:30 已写入 `wake_feed`，若 Cursor executor 未消费，21:45 fallback 前不会自动写稿推私聊；用户私聊相当于手动补唤醒
- 日报漏推补跑顺序：`prepare_daily_report_sync` → 写稿 → `post_daily_report_to_dm.py`（old-mac）；定稿落 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`
- 用户说「上传云端」须以其给的定稿**原封不动**上传；先更新本地报告文件再跑上传脚本，上传前不改字

