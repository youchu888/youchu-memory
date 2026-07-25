# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-25 · 最新归档：`sessions/tg-rotate-2026-07-25-1904.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 新 app 开归因：配置表**无行**时 ETL 白名单 JOIN 直接跳过，不是 `is_run=0` 能 UPDATE 的事，必须 **INSERT** `dim.dim_app_attribution_config`
- 只开计算、不开回写：`is_run=1`、`is_rewrite_channel=0`；**禁止**跑 `alter_table.sql` §4 那段 `UPDATE … SET is_run=0`，会把现网白名单全关
- 发布三处一致**：本地 `ops_system/` → **git commit + push（记 SHA）** → 海豚发布 → `live SQL` 与 `git show SHA:path` **diff 为空**；对外 bus/审单带 SHA（五档合表反例：海豚已 v137/v138、git 仍 4 表 → 野花 FAIL）
- [LESSON: attribution,prod-config|开通归因前先查配置表有无行；无行 INSERT、有行再 UPDATE；增量开通勿跑 bulk is_run=0]
- 设备加分统一口径：`brand_score=10`、`model_score=20`、`system_name=20`、`system_version=20`，`min_threshold=40`；时间档走 `dim_app_attribution_time_config` 的 **default** 四档（600/40、3600/30、21600/20、86400/10），新 app **不必单独插 time_config**
- 归因命中逻辑：IP + 24h 落地页主命中，设备四维 + 时间档加分，总分 ≥40 才 success
- 配置落 prod **不会补历史**；`result_d` 仍 0 时先查注册侧 `attribution_flag`，客户端开 flag 后再 **complement result**（当前无回写，不用跑 apply）
- `dim_user_attribution_channel_apply_d` 是海豚**回写任务名**（改 `dim_user_all.channel` 等），仅 `is_rewrite_channel=1` 才真写 channel；只算阶段可忽略
- **私聊要极简、群里要闭环**：用户只要 SQL 可只给 SQL，但配置执行后群里应主动一句进展（卡点 + 谁盯），避免「跟到哪了」才追
- 群聊/私聊回复先**接话再报数**，像同事聊天，少「· 第一点 · 第二点」汇报体；术语换成人话（如「只算、不写回 channel」）
- agent-bus 里 **野花/牡丹/千行/猫猫**（`mudan99` 等）与群里 @ 同等优先级，当天必回；Bot 互不可群 @，只能走 bus，**不能因私聊忙而漏回**
- TG 出站镜像标题曾写死「又初→狂人」；应按实际 `to_agent` 显示（`worker_ant`→狂人、`mudan99`→野花），改 `tg_task_tracker.py` / `agent_bus_send.py` / `agent_bus_watcher.py` 后需 **重启 tgbot**
- Paimon 影子 B 线（读 `paimon.dwd.*` 写 `_r`）：JOIN 字段类型不一致用 **staging CTE + CAST**；压测阻塞常见是湖侧 `attribution_flag` 全 NULL（SR 有数、Paimon 无）需采集/Flink 先落湖
- **发布三处一致**：本地 `ops_system/` → **git commit + push（记 SHA）** → 海豚发布 → `live SQL` 与 `git show SHA:path` **diff 为空**；对外 bus/审单带 SHA（五档合表反例：海豚已 v137/v138、git 仍 4 表 → 野花 FAIL）
- 本地 ETL 合表（4→2、`stat_grain=session|daily`）后，必须同步 dev session：outputs、related_tables、DDL/ETL、task.yaml；平台可能仍停旧结构，以 API 推 v2 为准
- test 闭环顺序：海豚发布 v2 task → 补跑 PI 成功 → T-1 验数 PASS → `request-publish` 绑 reviewer → 再通知审核
- 口径争议以 **prod 海豚线上 SQL** 为准，勿只看仓库；用户订单模型 `region` 用 `dim.dim_user_all` 注册地区（方案 A），非订单事件 IP/地理
- 星型六原则：事实优先、每源每 biz_dt 单次扫描、dim JOIN 克制、度量分型（UV 用 bitmap）、禁 SUM(日 UV)、列卫生

