# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-07 · 最新归档：`sessions/tg-rotate-2026-11-07-0652.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 溯源结论要落到**责任边界**：`dw` 是镜像，镜中无该事件时先找源头补事件，而不是先找 `dw` 表维护人。
- 私聊「上传云端」须以**已定稿 Markdown 原样**跑上传脚本，上传前**不得改写**正文。
- 日报定稿路径与 API 回执（如 inserted id）可记一句便于核对，**勿在记忆蒸馏中保留 token/密钥**。
- T-1/指定日 `datacheck` 在 prod 执行时，结论需带**环境、app_id、dt** 以便复现。
- 页面元素 CTR 日表 (`ads.ads_page_item_ctr_d`) 曝光为 0、点击有数时，往往是合并曝光/点击后聚合的**预期表现**，先要对照剧本与上游是否一致，别先判 ads 算错。
- 缺曝光的核对顺序：ads → `dwd_app_pageitem_exposure_d_r` → `dw.dw_user_event_detail_new`（看是否存在 `app_pageitem_exposure`），逐层确认是否**忠于上游**。
- 若 `dw` 里**完全没有**对应曝光事件名，而同日同 app 有点击、页面浏览等其它事件，优先归因为**该 App 未按协议上报曝光埋点**（客户端/SDK/业务接入），而非数仓或 fanout 单点丢数。
- 用**同日、同产品线其他 app** 对比（有的有曝光、有的没有），区分「单 App 漏打点」与「全链路/全 App 断流」两类问题，后一种才轮到接入/Flink/明细链路 owner。
- 表开发归属可查 dev session、`ops_system` 目录与 `task.yaml`（owner）；产发执行人与开发 owner 可分属不同角色，表述时分开。
- 页面点击率相关需求与补数、排查可在日报中合并为业务结果向一句话，避免堆砌内部代号与流水操作。
- 问「TG 保活挂了？」时先看 **tgbot dispatch 的 Telethon + `[visible-online]`**，不要只看 `com.youchu.tg-work-online`：后者进程可在跑，但 `.env` 里 `TG_WORK_ONLINE_ENABLED=false` 时自 10-17 起只是 idle，**不是现网绿点路径**。
- ACK 若返回 `dropped:silent`，**必须核对是否真发出**，不能默认已 ack。
- 同组 **dim 探针**改为两张 dwd_r 的 **`partition` 探针**；pb **直写正式表**、`sr_use_shadow=false`；改完 **cascade 回 S4** 再让审核重走 S7；**禁止手改 full_chain**。
- [LESSON: tg-green-dot|现网绿点只看 tgbot dispatch 的 visible-online 日志；Telethon watcher 异常退出则重启 tgbot，勿误判 tg-work-online launchd 为保活主路径]
- Bot API / 私聊能回，**不等于绿点在刷**；绿点断链时 dispatch watcher 已死，打卡与 `should_appear_online=True` 也刷不上绿点。
- 典型死因：Telethon 解析层报错（如 `Constructor ID 7600b9d3`）→ `[dispatch] watcher 异常退出` → 断连 → 之后 **`[visible-online]` 为 0**；用日志最后一条 visible-online 与时间戳定位断点。
- 恢复绿点：**重启 tgbot**（拉起 dispatch watcher）；私聊「重启 agent」在此语境下通常指重启 bot，不是只重启 Cursor。重启后核对新 PID、`visible-online online=True` 及 `/tmp/tgbot-dc.log`。
- 问「bus#N 在处理吗」：**查入站 → ACK → reply / processed**，以 reply 为准；已结案应明确报结案时间与 commit，避免让人以为还在跑。

