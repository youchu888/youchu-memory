# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-29 · 最新归档：`sessions/tg-rotate-2026-07-29-0601.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 群聊点名必回实质内容**：正文含「又初/初儿」、@ bot 或 @ 主人时，必须在群里给可验收答复；禁止「没@我」「群里不回」类推脱。
- bothub 未触发要重发新 id**：outbound 对方 poller 没拉到时，用**新 bus id** 重发（如 #5600→#5603），不要复用旧 msg_id；可在 bothub 按 `after_id` 核对 `to_agent=worker_ant`。
- DDL 改列勿用 IF NOT EXISTS 裸建**：`CREATE TABLE IF NOT EXISTS` 会**保留旧 schema**（例：`play_day_flag` 挡住新列 `is_eff_play`）；bootstrap 用 **`combined_N_ddl.sql` 全表 DROP+CREATE**，INSERT 补**显式列清单**，单表热修可单独 repair 脚本。
- 新 launcher 走 `_templates/`**：只填 `JOB` / `SQL` / `PROFILE`，调 `ops_system/_templates/spark_yarn_launcher.sh`；新 wf 先 **step0 DDL bootstrap** 再跑数据链，勿手抄 yarn 参数。
- [LESSON: device-tag,spark,ddl|Paimon/Spark 表结构变更时用 DROP+CREATE bootstrap，禁止仅靠 CREATE TABLE IF NOT EXISTS 期望新列生效]
- [LESSON: ops-system,templates,spark|新 Spark 任务 launcher 只填 JOB/SQL/PROFILE 走 _templates，wrapper 必须先 step0 DDL bootstrap 再跑数]
- **群聊点名必回实质内容**：正文含「又初/初儿」、@ bot 或 @ 主人时，必须在群里给可验收答复；禁止「没@我」「群里不回」类推脱。
- **bus 收件≠只有私聊 inbox**：发给猫猫/蓝猫审核线的 bus，又初可通过**协作群 TG 镜像**同步感知；答复时要区分「私聊 inbox 有无」与「业务上是否已收到」。
- **bothub 未触发要重发新 id**：outbound 对方 poller 没拉到时，用**新 bus id** 重发（如 #5600→#5603），不要复用旧 msg_id；可在 bothub 按 `after_id` 核对 `to_agent=worker_ant`。
- **设备标签不等狂人审阶段2**：知秋明确「设计/样例已给，先开发完 push git 再看」时，按 **library#46 + 姿态 F** 直接开阶段3，不阻塞在阶段2 HTML 审。
- **无 test 环境的标准交付**：Scala/Paimon 代码 + DDL 写完 → **push 配置库 `origin/dev`** → 群里发 **commit SHA + 改动路径** → 由狂人 **spark-submit** 跑数；又初不自 submit、不自验集群。
- **姿态 F 主链路**：`device_tag_wrapper.sh` 六步串行 ad→finance→video→active→dim→宽表，Paimon 落湖；DWM **中间3张有 dt**，dim/finance/宽表**无 dt 快照**；cron 挂 **user_tag wrapper 尾巴 UTC03:00**；lifecycle 用旧表 **9 档**，不加 network/screen/ua。
- **`dwm_device_tag_merge_pool_d_d` 是 v2 老线**：增量驱动池（delta/expiry/boundary），产物宽表是 `dws_device_tag_d_d`；**姿态 F step6 五表 JOIN，不经过 merge_pool**——被问表用途时要讲清「老架构 vs 当前 F 线」。
- **设备标签统一 Spark、海豚停更**：新开发/补数/验收只认 Spark wrapper；海豚 `wf_设备标签_日` 等 v1/v2（merge_pool、8 桶 UPSERT）为历史包袱，**跑通 F 后一并下线**，不在海豚修 SQL。
- **老海豚 P0 真错不修**：如 merge_pool preparedStatement 参数 bind bug，与「全迁 Spark」方向一致时，**不修海豚 SQL**，标「待 Spark 迁移下线」，与姿态 F 下线节奏合并处理。
- 群聊被 @ 又初/初儿**：必须给实质答复；禁止「没@我/群里不回」类推脱
- 设计链接是否收到**：先查 agent-bus inbox + 当日 TG 镜像；无记录则 bus 狂人问清 library URL / bus# / file_id，勿空猜
- [LESSON: device_tag,dim|device_id 空率≥90%（本需求 100%）则直建 dim_device_all，勿再设计 uid 反查兜底]

