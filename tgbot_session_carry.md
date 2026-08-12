# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-08-12 · 最新归档：`sessions/tg-rotate-2026-08-12-2043.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 群聊显式 @ 又初/初儿/@youchu_ai_bot 时，必须在群里给**实质答复**；禁止以「没@本机器人/群里不回」推辞。
- 大漏斗 session `dev-20260807-big-funnel-001` stage3：Spark 两阶段 ETL（metrics+wide）已跑通，SF-81 dt=2026-08-03 冒烟 spot-check PASS；开发侧卡点清完后等**集群全 app 压测**再补 stage4。
- 主人说「数据有问题/停了吧」→ **立刻 kill** YARN 任务并清本地 `run_yarn_daily_sql` 残留进程，再自查；未查清前不要重 submit。
- 说「你自己先查啊」= 不要等狂人回，主动查上游：SR 量级/小时分布、湖仓分区可读性、Flink fanout schema。
- 2026-08-11 停跑根因：Paimon **schema-6 事故**——`dwd_user_register_d_v2_r` 重建后 Flink fanout 仍写旧 schema，register 分区仅 ~8% 且不可读；video/novel/comic 同 fanout，湖侧整体不可靠；治本需重启 Flink fanout，狂人拍板前不再 submit。
- agent-bus 铁律：60 秒内 ACK → 干活 → reply 结案；正文丢失/仅「嘛」字要请对方重发完整问题。
- [LESSON: tg-group,协作|群聊显式 @ 又初时必须群内给实质答复，禁止以未 @ 机器人为由不回]
- 工作簿进展走**双通道**：群里自动发精简+详细，同秒 mirror 狂人（bus），`workbook_progress_posted.json` 记 `bus_sent=true`；编号要对齐团队簿项名（狂人 #6341 催过）。
- 集群试跑命令：`run_yarn_daily_sql.sh <dt> S SF-81 both`；先用 **S + 单 app**，别直接上 M/L；避开 **09:30~10:20** 避让窗；开跑必留 YARN `application_id` 和日志路径。
- 集群包路径 `/home/ec2-user/spark/big_funnel/`；SF-81 metrics 阶段墙钟约 **6 小时+**，RUNNING 长时间无日志输出在大 stage 里属正常。
- **集群代码可能与仓库不同步**：08-12 跑的是集群上 08-08 旧版单文件 SQL，不是 `origin/dev` 两阶段包；试跑前/重跑前应确认版本，跑完再同步最新 spark 包。
- **大漏斗读湖不读 SR**：prod SR 探表正常（行数、0~23 小时无断档）**不能**作为可跑依据；集群 ETL 读 Hive/Paimon。
- 工作簿编号映射（#6341）：3)→团队第 2 项归因段；9)/10)→第 1 项页面统计子项；设备标签（`dws_device_tag_d_d`）≠ 用户标签，不接管主人第 11 项。
- 协作群显式 `@youchu_ai_bot` / `@youchu8888` / `@又初` / `@初儿` 时，必须在群里给**实质答复**；禁止以「没@我」「群里不回」推脱。
- 群聊口吻学狂人：第一句给结论，短句口语、数字 inline；最多约 4 条 `·`；别铺 markdown 表格/`##` 标题，别写内心戏。
- 只有上述四种显式 @ 才回；裸写「又初/初儿」、只 @ 别人、标题带「又初→」——**一律不回**，且回复里不要解释为什么不回。
- 狂人 bus 派活若写明「结论请回 bus」，验完直接 `agent_bus_send.py reply` 结案；禁止问主人「要不要发 bus」。
- 团队唯一工作簿 canonical 在 `.claude/database/workbook.md`；进展播报应读 **`## 进行中`**，按**团队项名+编号**报，勿继续用狂人 TG 旧编号。

