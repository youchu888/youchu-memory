# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-09 · 最新归档：`sessions/tg-rotate-2026-08-09-0926.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 私聊 #283/#284 失败根因在 **Cursor 侧**（`--resume` 传输故障 / 云端 API 不可达），不是业务 SQL；排查时先区分基础设施 vs 任务逻辑。
- 大漏斗第 3 轮 executor OOM：`user_is_new` **JOIN 无分区 `dim_user_all`（~1.5 亿行）** 是根因；应改由**当日 `user_register` 推导**。
- 第 5 轮「跑通但 0 行」：源表 **`app_2556` 本身 0 行**，有效数据在 **`SF-81`（约 6022 万行）**；跑通 ≠ 成功，必须先核对 **app_id 与源表行数**。
- 用户说「直接检查错误原因」时：应出**根因表 + 当前状态 + 可补做项**（如补推日报、补跑 r5b），而非只复述失败现象。
- [LESSON: funnel-etl|user_is_new 禁止 JOIN 无分区 dim_user_all，改由当日 user_register 推导，避免 executor OOM]
- [LESSON: funnel-etl|宽漏斗禁单 SQL 宽聚合，拆成 metrics + wide 两阶段，避免 driver heap OOM]
- Bot 遇到失效 resume 会**按设计清掉旧会话**；用户可重发指令或发「重启 agent」强制新开。
- 任务 18:13/18:33 入队、23:35 才跑并失败，说明中间是 **Cursor 卡住/排队**，不能据此判断又初未执行。
- 日报 API 中断时：本地草稿可能已在 `~/.dc-platform/memory/work-log/hosts/*/reports/`，但 **TG 推送与云端上传会漏**；恢复后需补推、补传。
- 第 4 轮 driver heap OOM：单文件宽聚合导致计划树过大（`TreeNode.generateTreeString`）；**弃用单 SQL 宽聚合**，改拆分链路。
- **r5b（SF-81）两阶段 ETL**（metrics ~6.3h + wide ~17s）已验证无 OOM；宽表粒度 `(dt, app_id, is_new)`，dt=2026-08-03 产出 **3 行**符合预期。
- 群聊里 `@worker_ant_bot` 派给猫猫的 `ads_product_day_stat_d` 改动（video_play 从 dwd 换 dwm）是**旁听背景**，与本会话大漏斗/日报排查无直接执行关系。
- stage37 OOM 根因是单条超宽 `COUNT(DISTINCT CASE...)` 同时在单个 stage 维护过多 distinct 集合，内存峰值过高。
- 重构 ETL 时必须同步三处文档：`spec.md`（口径）、`design.md`（数据流/实现）、`memory.md`（进展与待验项），避免代码与口径脱节。
- [LESSON: spec|口径|is_new] 临时口径与目标口径并存时，必须在 spec 写明当前实现来源与未接入的上游（如 `dim_user_daily_snapshot`），避免验数按错标准。
- 大漏斗任务工作目录固定为 `ops_system/04.dws/dws_app_event_funnel_d_d/`；续做前先读 `spec.md` / `design.md` / `memory.md` / `task` 定位卡点，再动 SQL。
- 抗 OOM 改法：把「一条大聚合」拆成「按事件独立聚合 + 以 keys 外连接拼宽表」；先保口径不变，再验可跑性。
- 当前 Spark 版 `is_new` 临时口径：以当日 `user_register` 事件推导，不用 `uid=-1`；目标来源是 `dim_user_daily_snapshot`，但现阶段不直连，需在 spec 里显式标注。

