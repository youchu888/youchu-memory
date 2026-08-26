# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-27 · 最新归档：`sessions/tg-rotate-2026-08-27-0651.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 「注册事件」在脏表里事件名是 **`user_register`**，不要未经核对就混写 `register` / `user_register`。
- 第一遍 SQL 列名/事件名写错时，**立刻改 SQL 重查并交付**，不要只解释或重复「在查」；被问「变傻了」时简短认错 + 说明已修正即可。
- [LESSON: paimon,dirty_data,sql|查 `dwd_standard_dirty_data_df` 前先对元数据，禁用臆测列（如无 `create_time`）；注册事件用 `user_register`，勿混 `register`]
- 查 **Paimon 脏表**（`paimon.dw.dwd_standard_dirty_data_df`）前，**先对元数据/列名**再写 SQL；该表**无 `create_time`**，可用 `process_time`。
- 标准流程：**先条数**（`COUNT(*)` + `COUNT(DISTINCT event_id)` 看是否重复），**再导明细 CSV**；条数群里报，文件自动发。
- 脏数据明细常用列：`dt, app_id, event, event_id, event_time, error_type, error_column, error_value, record_level, target_table, source_table, error_info_list, raw_data, process_time`。
- 排查注册脏数据时，用 `get_json_string(raw_data, '$.payload.type') AS payload_type` 看 payload 类型。
- 本次 TSYH-002（`dt=当天`）`user_register`：**4115 条**，`event_id` 去重也是 4115，**无重复**。
- 4115 条共性：全是 **`payload.type=device`**；拦因统一 **`dictValues` / 字段 `type`**（注册 type 不在字典里被清洗）。
- 过滤条件模板：`dt = '业务日' AND app_id = 'TSYH-002' AND event = 'user_register'`；明细按 `event_time, event_id` 排序导出。
- 用户说「按照这个上传云端」时，以粘贴的日报正文为唯一准绳：先落本地定稿，再上传，正文禁止改写或润色。
- [LESSON: daily-report|用户确认「传好了是吧」类追问时只复报日期/云端 ID/状态，勿重复执行 upload 脚本]
- 本地定稿固定路径：`.cursor/work-log/reports/日报-YYYY-MM-DD.md`；上传命令：`.cursor/scripts/upload_work_report.py --date YYYY-MM-DD`。
- 上传成功回执至少带三项：日期、云端记录 ID、状态（`inserted` 新建 / 覆盖更新）；便于主人核对与留档。
- 用户追问「传好了是吧」时，一句肯定 + 复报日期/ID/状态即可，不必重复跑上传脚本。
- 若本地已有同日定稿，仍按用户新贴正文覆盖后再传，保证云端与主人给定稿一致。
- 2026-08-25 指标库 v0.3 当日交付：ER 图定稿（指标/维度/实体边界）、设计稿推数据开发平台文档库、一期建表与角色种子草案就绪。
- 续做 TOP1（截止 08-27）：按 v0.3 定稿推进建表、元数据与联调落地。

