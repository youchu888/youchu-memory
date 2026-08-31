# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-01 · 最新归档：`sessions/tg-rotate-2026-09-01-0626.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 日报「上传云端」须以定稿 Markdown **原封不动**落盘（`.cursor/work-log/reports/日报-YYYY-MM-DD.md`）再跑 `upload_work_report.py`，禁止改写后再传
- Spark SQL 硬规矩：源表用 `_r` 版；`_r` 数值列 VARCHAR 须 CAST；天表只 `WHERE dt='${DT}'`；必须幂等；paimon 列顺序对齐；验收先 `run_test.sh run --step=... --explain`，**别动生产 `full_chain.json`**
- 大漏斗按已定稿口径写：`docs/event_dictionary_big_funnel_20260801.html` + 平台 `metric_big_funnel_event_dictionary`；仓库骨架在 `ops_system/04.dws/dws_app_event_funnel_d_d/spark/`（metrics + wide 两阶段），不重开口径
- agent-bus 派单：同一 Cursor 主会话处理，**60 秒内 ACK → 干完 reply 结案**；reply 成功前不 mark 结案；引用历史结论前须核对是否已被后续决策作废（如设备标签 #7735 过期说法）
- [LESSON: prod-monitor,oncall|prod 告警处置顺序：先分 env → 问此刻是否仍在发生（DS state=1，不信 monitor 快 1h 的时间戳）→ 追首个 FAILURE 真 task → download-log 取证，禁信根因字段与 DEPENDENT]
- [LESSON: spark-scheduler,pipeline-runner|加 Spark 任务只改 SQL + steps.json 挂槽位，tagTargets 必填，先 explain 试跑，禁止动生产 full_chain.json]
- Spark pipeline-runner **加任务 = 写 SQL 文件 + 在 `steps/full_chain.json`（或独立测试 json）追加一步并挂到 group/槽位**；驱动不认业务，**不改 Scala**
- 调度三层：`slots`（整点跑哪些组）→ `groups`（组内步顺序）→ `steps`（步定义）；Step 必填 `name/unit/trigger/probes/impl/params.sqlFile`，**`tagTargets` 必填**（回滚凭据）
- 设备标签：08-04「不上 prod」**作废**；08-11「捡回来」+ 知秋确认拦阻已解除，现状是 **等 pipeline-runner 就位后接上**；又初主责按规范改造
- 设备标签硬约束：主键/join 一律 **`device_fingerprint`（64 位，不看 fp_version）**；`device_id` 仅附属；六张 dwm + dim + dws + uid_map 全链改键
- 设备标签现状：paimon 建齐但数据停在 **07-27**；enroll 闸门从未生效；`dwm_device_uid_map_d` **只有 spec 无 SQL**；交付 **先出方案审过再动手**，方案须答指纹替换清单/覆盖率、`_r` 50 天保留、enroll 闸门+人口预估、uid_map SQL、pipeline-runner step 五问
- prod 值班六条：① **先分 env**，test 断流/僵尸 wf **一律不处理**；② 先问「**此刻还在发生吗**」（server_monitor 时间戳比 DS **快 1 小时**，须回 DS 查 **state=1**）；③ **DEPENDENT/「等_xxx」是果**，只追首个 **state=FAILURE** 真 SQL task；④ **禁信 server_monitor 根因**，用 `download-log?taskInstanceId=` 取证，**不用** `/log/detail`（会截断）；⑤ 行数涨跌跟**前一日同小时**比；⑥ 可能已自愈，看**当时**实例/日志
- **直接修复半径（知秋授权）**：判为 **prod 事故** → 立即处置（**含改代码**），处理完再报，事故窗口内不停下来请示；**非事故**的日常 prod 变更/口径设计/加表加字段 → 照旧等知秋 GO；先用六条判是不是事故，不确定先查清楚
- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 「上传云端」与写日报、推 TG 是**独立指令**；主人单独说时才执行，写稿/推 TG 后**禁止**自动上传
- 口语「按这个上传云端」= 以**已定稿**日报为准，**不重新生成、不改写**正文
- 上传铁律：**原封不动**——禁止润色、补字、改格式后再传
- 定稿路径：`.cursor/work-log/reports/日报-YYYY-MM-DD.md`；未指定日期则用当日（Asia/Shanghai）

