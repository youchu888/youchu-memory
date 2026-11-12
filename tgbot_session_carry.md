# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-13 · 最新归档：`sessions/tg-rotate-2026-11-13-0605.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- TG/Cursor 派活带大 `prompt_*.md` 时：先读启动包，再通读该文件并定位末尾「当前问题」；按问题执行，禁止只复述 prompt。
- 对同一 `reply-to-bus-id` 的实质回执若被出站去重拦截，可用 `--no-dedup` 重发；仍须带可查证的核数结论，勿空「已知悉」。
- 运维回执类任务（如「alter 六句已执行」）：出口统一走 `agent_bus_send.py`，`--reply-to-bus-id` 对齐原派单（如 bus#13263），结案用 `kind=reply`。
- SR 影子表 DDL 完工回执前：prod 只读轻量验收——列总数 + 目标列名与列序，再发 bus；必要时附 `SHOW CREATE TABLE` 或等价列清单。
- 本例验收表：`dws.dws_register_attribution_result_d_paimon_shadow`；六列为 `score_brand / score_model / score_system / score_system_version / score_time / time_bucket_max_seconds`（与 35 列总量、列序一并核对）。
- 正文对外写业务主人名（知秋），技术上记清新 outbound bus id（如 #13275）与所回复 bus id 的对应关系，便于对账。
- 类似 bus#13263「影子 ALTER 已跑完 → 告知狂人」：先查库后发言，避免未验收就结案。
- 小时任务挂用户属性（知秋已定）**：只读 `dwm.dwm_user_attr_intraday_d_d`，`dt='D'`，按 `(app_id, uid)` LEFT JOIN；**禁止**小时格读 `dim.dim_user_snap`。
- `dim_user_snap` 单分区约十八亿行，小时任务每格全扫一次约多花 3 分钟+，是禁用的性能根因。
- 跨 owner 小时 SQL 仍可能旧口径：本名下无改动则 reply 写清「名下无小时 join snap」+ 点名旁观文件交给对口 owner，勿越权改他人稿。
- [LESSON: etl,hourly,user_attr|小时挂用户属性仅用 `dwm_user_attr_intraday_d_d` dt=D；禁小时读 `dim_user_snap`]
- 验「测试海豚能否登录」应双线：`/dolphinscheduler/ui/login` 可达（HTTP 200）+ MCP/API 鉴权成功且能列出项目（如运营系统、渠道系统）。
- 大号 TG prompt 文件：读开头指令与末尾「当前问题」，直接答问题，避免复述全文。
- 测试海豚入口形态：`http://<test-host>:12345/dolphinscheduler/ui/login`；默认 UI 账号为 `admin`，密码见本地 dolphin 配置或知识库，**蒸馏/lesson 不写明文密码**。
- 私聊要账号密码：从仓库内 test 海豚配置核对后回复；回复前宜先 UI/API 实测登录成功再交付。
- **小时任务挂用户属性（知秋已定）**：只读 `dwm.dwm_user_attr_intraday_d_d`，`dt='D'`，按 `(app_id, uid)` LEFT JOIN；**禁止**小时格读 `dim.dim_user_snap`。
- 旧说明「小时先 snap D-1 再叠日间表」作废；天任务仍用 `dim_user_snap` / `snap_dt=D`（或 D-1 按既有天任务口径）。
- 日间表可直接取：渠道、注册时刻、地区、设备、VIP、uid_code；编排上日间表应在同格先跑完再被小时消费。

