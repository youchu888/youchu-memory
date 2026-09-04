# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-04 · 最新归档：`sessions/tg-rotate-2026-09-04-1247.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- `_h_r` 做天计次必须用 **`COUNT(DISTINCT event_id)`**，且 `dt` 用裸串；这是狂人复审三条里的硬检查点
- 沙箱跑数前必须 **同步集群 SQL**；本地已 push 但集群还是旧版时，yarn 壳/SQL 宏会对不上
- 今天收口路径：explain PASS → 去 `--explain` 真跑 metrics→wide → 验 `test.dws` 宽表有行且 `sdk_init/video` 非全 0
- 催狂人审改 SQL 时，模板要带：**commit、文件路径、选表/计次规则摘要、请回 PASS 或打回点**；bus 已发过仍可在群里补一句
- [LESSON: 大漏斗|摘 new 改 stage_metrics 时 _h_r 天计次固定 COUNT(DISTINCT event_id)，legacy daily.sql 用 task.yaml disabled 冻结勿删]
- 大漏斗摘 `new` 的卡点常不是 `_r` 表有没有，而是 **#7880 改造清单/选表规则是否对齐**；表齐（如 `dwd_sdk_init_d_r`）只代表最后一环就绪，不等于整链可改 SQL
- 主人拍板「我们自己干」后，可按 **#7880 已透出的选表规则** 先改 `stage_metrics`，不必死等狂人统一清单；改完 push 并 bus 请审即可
- 主干改造范围：`stage_metrics` 里 **11 个主干事件 + page_view** 全切 `paimon.dwd.*_r`，**零引用** `dw.dw_user_event_detail_new`
- 选表口径：`register/login` → `*_v2_r`；`order_paid` → `d_r`；`sdk_init` → `dwd_sdk_init_d_r`；`order_created/coin` 等小时表 → `_h_r`
- **legacy `daily.sql` 冻结不投**：仍含 `new`，主线只动 `stage_metrics`；冻结方式是 **仓库保留 + `task.yaml` 显式 `disabled`**，不是删文件
- 开干前先 **prod 实查 `_r` 表**：表在不在、当日分区行数是否合理（新表昨日分区为 0 很常见）
- 狂人 bus 复审（如 #7900）可与出数 **并行**：「等 #2287 落地后再复审」**不挡** 今天 SF-81 沙箱 explain / test 出数
- agent-bus **ACK 可能被服务端 silent 丢弃**；实质回执靠 reply 结案，必要时 ACK 用 `--no-dedup` 重发
- 主人问「日报怎么不发了」时，先区分是 **TG 没推** 还是 **云端没传**，再对症查；勿把私聊补传云端当成 TG 推送已恢复
- 主人私聊贴定稿正文并说「上传云端」→ **原封不动**落盘到 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`，再上传；上传前禁止改字
- 私聊补传场景：TG 定时未触发时，主人可直接贴已定稿日报走云端上传；两条线可并行缺失、分别补救
- `apply_tgbot_workbook_no_instant_ack.sh` 用于 tgbot workbook「禁即时 ack」类配置变更；与日报推送无直接耦合，别混为一谈
- 日报有**两条独立链路**：TG 私聊自动推送（old-mac 定时 `post_daily_report_to_dm.py`）与「上传云端」（主人指令后跑 `upload_work_report.py`）；一条没触发不代表另一条也停

