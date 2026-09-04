# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-04 · 最新归档：`sessions/tg-rotate-2026-09-04-2115.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 大漏斗沙箱 **explain PASS ≠ 已出数**；explain 结束后必须立刻接 metric 真跑 → wide 真跑，中间不能停，否则 `test.dws` 宽表仍 0 行
- `hadoop-1` 直连常被拒，查 explain/YARN 实况应走**已知入口**，不要死磕直连
- 狂人 **stage_metrics 复审**对象：`563013e7` + 冻结 tag `8b613fb6`；PASS 5 条含 11 张 `_r` 全切、`${DT}` 裸串、18 路 `COUNT(DISTINCT event_id)`、`reg_uids` 换 `dwd_user_register_d_v2_r` 等
- 长时间无回可先查是否已有 reply，再发 **bus 催促**（如 #7911），写明「今天要出数、请优先审」+ 当前 test 进展 + 还差什么 PASS/打回
- [LESSON: funnel|explain PASS 后同一轮会话内立刻接 metric→wide 真跑，开跑前确认源表 T-1 分区有数且 `--dt` 任务日与业务日对齐]
- [LESSON: agent-bus|狂人侧消息常被压缩截断，reply 须贴回 #7900 等待审原文一字不动并写明 commit+tag，勿让进度汇报冒充复审单]
- 真跑前先核对 **源表分区有数**（如 `sdk_init` 只有 `09-04` 有分区）再开跑，避免空跑
- 大漏斗 `--dt` 是**任务日**，业务数据段 = T-1：任务日 `2026-09-05` → 业务日 `2026-09-04`，须与源表分区对齐
- 出数链路固定顺序：`dws_app_event_funnel_metric_stg_d`（stage_metrics）→ `dws_app_event_funnel_d_d`（stage_wide）；验 `sdk_init`/`video` 非全 0
- **#7900 复审不挡当天 test 出数**；可先冒烟/真跑，复审并行
- agent-bus 出站 `#7908` 等是 **reply 结案回执**，不是又初另起一单；收到 work 单 → 60s 内 ACK → 干完 reply
- 狂人侧 **上下文会被压缩丢原文**（#7906/#7900/#7911 均发生过）；reply 时须把待审/待确认内容**一字不动贴回**（纯文字、三条到齐），并明确复审对象 commit+tag
- 进度汇报（#7906 出数成功）与复审请求（#7899/#7900 三条）要**分开表述**，避免对方误当复审单
- 主人分工：**又初负责 test 全量跑到位**（非 SF-81 单 app 冒烟，`app_filter_e/v/n/c` 全空串全 app），狂人验数 → 挂调度 → 回写；用 `sandbox_steps_full.json` 槽 00，命令按 `_meta`「怎么跑」三行
- test 出数落 **Paimon `lakehouse_test`**；SR 尚未同步属预期，不等 SR 再报 progress
- `_h_r` 做天计次必须用 **`COUNT(DISTINCT event_id)`**，且 `dt` 用裸串；这是狂人复审三条里的硬检查点
- 沙箱跑数前必须 **同步集群 SQL**；本地已 push 但集群还是旧版时，yarn 壳/SQL 宏会对不上
- 今天收口路径：explain PASS → 去 `--explain` 真跑 metrics→wide → 验 `test.dws` 宽表有行且 `sdk_init/video` 非全 0

