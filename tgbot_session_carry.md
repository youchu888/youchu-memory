# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-25 · 最新归档：`sessions/tg-rotate-2026-10-25-1311.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 私聊问「值班有没有异常」→ 先对值班日历，再按 **pipeline-runner 值班 SOP** 查调度 heartbeat + 当日真实告警，不要凭 inbox 印象下结论。
- 用户要深入时：可选 **盯该格** 或 **按 runbook 核 HDFS 完成标记** 再决定是否补数，勿未核就动手补。
- **真故障** vs **链路测试**：`runner_link_test`（如 bus 链路测试）不算故障；要区分 inbox 里 **`runner_` 前缀的真实告警** 与测试/演练消息。
- 调度器健康三件套：**daemon 在跑**（pid）、**log 新鲜度**（如 `log_age_sec` 很小）、**近期错误计数**（如 `err_count_recent=0`）。
- 各线状态 **`idle` / `slot_done`** 且 **同一步骤 >20 分钟无进展** 才算卡死；仅 `wait_probe` 不算跑挂。
- 顶层 **`block_reason: 探针未放行: <表>`** 且主链仍是 **`slot_done`** → 归类为 **探针等待**，不是 ETL 失败。
- **`wait_probe` 挂账**：从今天 08:00 起等上游探针放行时，**默认观察、不立刻补数**；挂账链会自续，**只有长期不动或反复失败** 才走补数/runbook。
- 挂账常 **连带 pending**：前一格（如 `dt#08`）未了结 → 下一格同挂（`pending_count` 可 >1），汇报时要写清 **卡点格 + 连带格**。
- 例：`dws_app_coin_consume_d_h` 在 `wait_probe` 时，需同时看 **上游探针表**（如 `dwd.dwd_video_event_h_r`）是否未放行。
- 问「Spark 跑完没 / 三表有数没」时，不要只看 prod SR 行数；应串联 **prod SR → prod Paimon → 生产 `full_chain.json` 是否挂任务 → dev session 是否已产发 → 上游 snap**。
- 对外结论宜拆两层：**基础设施/上游就绪**（表建好、snap 有数） vs **Spark 三表未挂产/未跑**（产 SR/Paimon 全空）；避免只说「没跑完」造成歧义。
- **prod SR 与 prod Paimon 同为 0 行**，可判定 Spark 链路**从未在产写出过数**（不是「跑慢」或「只没落 SR」）。
- 任务只在 **`full_chain_testcluster` 测试编排**里、**生产 `full_chain.json` 无对应节点** → 产上**根本没挂 Spark 跑**，与「任务失败」要区分开。
- **test SR 有数**（如部门月/周、产品周）可能是**旧海豚口径**；**不能**当作「prod Spark 已跑通」的证据。
- 表按日期重建完成、上游 **snap 已有数**（如 `snap_dt=2026-10-23`），**不自动**代表下游 ADS 三表会有数；中间还缺 **挂产 + 跑批 + 产发**。
- 管理报表三表常一起核对：**`ads_dept_promotion_summary_m` / `_w`**、**`ads_product_promotion_summary_w`**。
- session 停在 **stage7** 且 **`publish_runs_count=0`** → **尚未产发**；产表为空在此状态下是**预期**，不是偶发缺数。
- 要出数的路径：**审核通过（如 `ad004aed`）→ 挂生产 Spark 编排 → 跑批**；或经审批的**手工补跑**，不能假设 snap 好了会自动出 ADS。

