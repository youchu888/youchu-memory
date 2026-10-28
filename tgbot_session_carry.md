# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-28 · 最新归档：`sessions/tg-rotate-2026-10-28-2210.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 写日报前铁律顺序：**先双机 upload + sync，再汇总**；跳过 sync 直接写稿会表现为「缺某台机的活」。
- 会话里助手连续返回「模型额度可能已用尽」且走完整 fallback 链，说明**复杂对话层被挡**；主人反馈「token 还有很多」时，应区分 **Cursor 模型路由/额度** 与 **TG Bot 侧 token**，勿用同一句模板搪塞业务问题。
- 私聊再次强调：**对外表述禁止「狂人」「产发」等内部/机器人化用词**；派单归因用主人名（如知秋），日报与私聊同一套称谓规范。
- 该摘录**没有给出同步问题的实际排查结论**（全为额度拦截回复），蒸馏时只保留「该怎么同步 + 别用错误话术」，不编造已修复原因。
- [LESSON: user-facing-words|私聊/日报/回执禁用「狂人」「产发」等内部词，派单与协作说法用主人名与业务任务名]
- [LESSON: model-quota-vs-task|遇全链 fallback 额度提示时，简短说明对话模型受限，同步/查数类问题仍按 runbook 逐步答，勿重复空模板忽略主人原问]
- 主人问「old mac 干的活儿为什么没同步」，本质是**双机工作记录未进同一套 memory 链路**，不是 Cursor 会话会自动跨机。
- Cursor **agent transcript 不跨机**；另一台机器上的交付若只留在本机 transcript，对侧 Agent/日报**默认看不见**。
- 可复用的同步路径：**本机写入** `.cursor/work-log/当日.md`（或 ops-mirror 兜底）→ 跑 **`sync-memory-git`** 推到 youchu-memory → 对侧 **`prepare_daily_report_sync.sh`** 再读合并稿 `~/.dc-platform/memory/work-log/YYYY-MM-DD.md` 与各 `hosts/*/`。
- 若 `hosts/new-mac` / `hosts/old-mac` **缺当日文件**，回复里应**点明缺哪台**，不能假装已双机齐全。
- 额度告警场景下仍应保证：**心跳/查数/SQL** 等通道可用，但**不能替代**对同步问题的具体排查与说明。
- 私聊问「值班有没有异常」→ 先对值班日历，再按 **pipeline-runner 值班 SOP** 查调度 heartbeat + 当日真实告警，不要凭 inbox 印象下结论。
- 用户要深入时：可选 **盯该格** 或 **按 runbook 核 HDFS 完成标记** 再决定是否补数，勿未核就动手补。
- **真故障** vs **链路测试**：`runner_link_test`（如 bus 链路测试）不算故障；要区分 inbox 里 **`runner_` 前缀的真实告警** 与测试/演练消息。
- 调度器健康三件套：**daemon 在跑**（pid）、**log 新鲜度**（如 `log_age_sec` 很小）、**近期错误计数**（如 `err_count_recent=0`）。
- 各线状态 **`idle` / `slot_done`** 且 **同一步骤 >20 分钟无进展** 才算卡死；仅 `wait_probe` 不算跑挂。
- 顶层 **`block_reason: 探针未放行: <表>`** 且主链仍是 **`slot_done`** → 归类为 **探针等待**，不是 ETL 失败。
- **`wait_probe` 挂账**：从今天 08:00 起等上游探针放行时，**默认观察、不立刻补数**；挂账链会自续，**只有长期不动或反复失败** 才走补数/runbook。

