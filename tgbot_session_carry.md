# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-01 · 最新归档：`sessions/tg-rotate-2026-09-01-1113.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- prod 盯盘口径是**告警驱动**，不是又初另起一套夜间全量巡检；检测已在 `server_monitor`（54.255.236.159），禁止再造监控
- 长任务按主人要求**定时私聊汇报**；卡点一次性列清选项私聊拍板，不要边做边猜
- [LESSON: device-fingerprint|设备标签/uid_map 主键用 device_fingerprint，无指纹丢弃；改造顺序 uid_map→dim/dwm/dws，以 bus#7738 覆盖旧 prod 禁令]
- 收到 **env=prod** 告警后固定链路：先验「此刻还在不在」→ 定位真失败 SQL → `download-log` 判因 → 从 playbook `part_01` 起处置
- bus#7742 事故授权：**确认是事故可立刻修（含改代码），修完再报**；日常非事故变更仍等知秋 GO
- 值班安排是又初+牡丹搭班，狂人下发六条判据与修复半径；没接到告警就不动，但告警漏接算值班未站稳
- 约定变更后须同步改 `MEMORY_OPEN` / playbook / feedback，并推到 youchu-memory 供双机拉齐
- Spark 加任务（bus#7735）：**只写 SQL + `steps.json` 挂槽位，不改 Scala**；源表用 `_r`、数值列入口 CAST、`tagTargets` 必填、`${DT}`/`${OUT_DB}`、行为键 `UPPER(TRIM)`
- 挂槽改造先用沙箱 `steps/sandbox_steps_fragment.json`，**未验证前别动 prod `full_chain.json`**
- 设备标签（bus#7738）：主键改 **`device_fingerprint`**，`device_id` 仅附属；无指纹行丢弃；拦阻已解除，等 pipeline-runner 接上
- bus#7738 覆盖了 #7735 里「先不上 prod」的过期说法，以较新交底为准
- 多步改造默认顺序：先落地缺的 **`uid_map`** → 再改 dim / 六张 dwm / dws 宽表 PK
- dim 重建若 `_r` 只保留约 50 天，07-13 前沉默设备的 `last_login_time` / `last_active_time` 需业务拍板（置空 / 保留旧 dim / 只认近 50 天）
- 日报「上传云端」须以定稿 Markdown **原封不动**落盘（`.cursor/work-log/reports/日报-YYYY-MM-DD.md`）再跑 `upload_work_report.py`，禁止改写后再传
- Spark SQL 硬规矩：源表用 `_r` 版；`_r` 数值列 VARCHAR 须 CAST；天表只 `WHERE dt='${DT}'`；必须幂等；paimon 列顺序对齐；验收先 `run_test.sh run --step=... --explain`，**别动生产 `full_chain.json`**
- 大漏斗按已定稿口径写：`docs/event_dictionary_big_funnel_20260801.html` + 平台 `metric_big_funnel_event_dictionary`；仓库骨架在 `ops_system/04.dws/dws_app_event_funnel_d_d/spark/`（metrics + wide 两阶段），不重开口径
- agent-bus 派单：同一 Cursor 主会话处理，**60 秒内 ACK → 干完 reply 结案**；reply 成功前不 mark 结案；引用历史结论前须核对是否已被后续决策作废（如设备标签 #7735 过期说法）
- [LESSON: prod-monitor,oncall|prod 告警处置顺序：先分 env → 问此刻是否仍在发生（DS state=1，不信 monitor 快 1h 的时间戳）→ 追首个 FAILURE 真 task → download-log 取证，禁信根因字段与 DEPENDENT]

