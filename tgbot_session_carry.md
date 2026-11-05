# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-06 · 最新归档：`sessions/tg-rotate-2026-11-06-0652.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 问「TG 保活挂了？」时先看 **tgbot dispatch 的 Telethon + `[visible-online]`**，不要只看 `com.youchu.tg-work-online`：后者进程可在跑，但 `.env` 里 `TG_WORK_ONLINE_ENABLED=false` 时自 10-17 起只是 idle，**不是现网绿点路径**。
- ACK 若返回 `dropped:silent`，**必须核对是否真发出**，不能默认已 ack。
- 同组 **dim 探针**改为两张 dwd_r 的 **`partition` 探针**；pb **直写正式表**、`sr_use_shadow=false`；改完 **cascade 回 S4** 再让审核重走 S7；**禁止手改 full_chain**。
- [LESSON: tg-green-dot|现网绿点只看 tgbot dispatch 的 visible-online 日志；Telethon watcher 异常退出则重启 tgbot，勿误判 tg-work-online launchd 为保活主路径]
- Bot API / 私聊能回，**不等于绿点在刷**；绿点断链时 dispatch watcher 已死，打卡与 `should_appear_online=True` 也刷不上绿点。
- 典型死因：Telethon 解析层报错（如 `Constructor ID 7600b9d3`）→ `[dispatch] watcher 异常退出` → 断连 → 之后 **`[visible-online]` 为 0**；用日志最后一条 visible-online 与时间戳定位断点。
- 恢复绿点：**重启 tgbot**（拉起 dispatch watcher）；私聊「重启 agent」在此语境下通常指重启 bot，不是只重启 Cursor。重启后核对新 PID、`visible-online online=True` 及 `/tmp/tgbot-dc.log`。
- 问「bus#N 在处理吗」：**查入站 → ACK → reply / processed**，以 reply 为准；已结案应明确报结案时间与 commit，避免让人以为还在跑。
- agent-bus **60 秒内 ACK** 是硬要求；入站后十余分钟才 ACK 会被主人判为偏慢，即使活已干完也要在回复里说明时间线。
- 点击率 `dev-20261020-002` 上 S7：生产无 `g_page_item_ctr` 前，S4 须先改编排——**摘掉**旧方案 `dwd_app_pageitem_d_r`（合表、读 `dw_user_event_detail_new`，生产无此表）；明细以 fanout 两张 dwd_r 为准。
- 生产建组验收步（挂 11 槽示例）：`dim_app_page_item_d` → `ads_page_item_ctr_d` → `pb_dim` → `pb_ads`；建组由知秋侧，野花按指定 commit 重走 S7。
- 双机记忆拉齐：old-mac 跑 `prepare_daily_report_sync` / `sync-memory-git`；核对 **new-mac / old-mac 当日 hosts** 与远端 main；双机同时 push 可能 rebase 冲突，需重推；未入库 lesson/pinned 要一并推远端。
- 主人要求：**遇到的问题都要沉淀**；并行长任务占一路 agent 时，另一条私聊应冷启动读记忆独立答，避免只报「还在跑」。
- 代主人发 TG 群：先私聊贴改稿等确认，未确认前禁止发群、禁止重复发。
- 群消息忌 AI/知识库腔（「正在检索」「上下文整理」「已沉淀」等），宜短句、口语、先结论。
- 忌工单腔（【背景】【请你做】【不做】）；宜对齐主人日常（如 `@xxx 生产执行下`、老哥麻烦…）。
- 事说清即可，忌「定了@我」「好了@我」等收尾；可日常读 TG 学主人群聊口吻。
- 推广周表改源：须 spark+SR 共 4 份 SQL、两份 task.yaml、compare 报告一并 commit 并 push 到 origin/dev，否则不进审核。

