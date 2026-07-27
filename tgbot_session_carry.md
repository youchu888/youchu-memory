# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-27 · 最新归档：`sessions/tg-rotate-2026-07-27-1851.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 没 @ 初儿时**静默跳过**，群里**不要**写「这条没 @ 我」「我不插嘴」之类内心戏。
- 群聊口吻学工作狂人：第一句就是结论/在干啥，短句口语，数字 inline，别铺 wiki 式长文。
- 群聊**禁止**用 `##` 标题、markdown 大表格；真要列点用 `·` 或换行，**最多 4 条**。
- 狂人 bus 写明「结论请回 bus」→ 验完**直接 agent-bus reply 结案**，别问主人「要不要发 bus」。
- 群里你是 **初儿**（`@youchu_ai_bot`）；**又初**是主人真人名，**禁止**让同事 @又初。
- 私聊可以长，群聊让人**扫一眼就懂**；验数/派活结论走 bus，群里只做轻量同步。
- `[LESSON: tg-group|bus-reply|bus 派活要求「结论请回 bus」时，验完直接 agent-bus 结案，禁止再问主人是否发送]`
- 群聊里先看 `@` 对象：@的是 `@mudan99_bot`（野花）就**不回**；只有 @ `@youchu_ai_bot`（初儿）才接活。
- 对方 @ 你已带背景时，**别整段复读** bus/派单正文。
- bus 结案后，群里可 **@ 提问者一句带过**（例：「bus#1421 已回狂人，初步 OK」）。
- `ads_product_day_stat_d` 订单创建/支付成功笔数金额口径，本次是问野花侧报表，不是又初群聊职责。
- `[LESSON: tg-group|mention-routing|未 @youchu_ai_bot 的群消息直接不回，且不在群里解释「为什么不回」]`
- 新 app 开归因：配置表**无行**时 ETL 白名单 JOIN 直接跳过，不是 `is_run=0` 能 UPDATE 的事，必须 **INSERT** `dim.dim_app_attribution_config`
- 只开计算、不开回写：`is_run=1`、`is_rewrite_channel=0`；**禁止**跑 `alter_table.sql` §4 那段 `UPDATE … SET is_run=0`，会把现网白名单全关
- 发布三处一致**：本地 `ops_system/` → **git commit + push（记 SHA）** → 海豚发布 → `live SQL` 与 `git show SHA:path` **diff 为空**；对外 bus/审单带 SHA（五档合表反例：海豚已 v137/v138、git 仍 4 表 → 野花 FAIL）
- [LESSON: attribution,prod-config|开通归因前先查配置表有无行；无行 INSERT、有行再 UPDATE；增量开通勿跑 bulk is_run=0]
- 设备加分统一口径：`brand_score=10`、`model_score=20`、`system_name=20`、`system_version=20`，`min_threshold=40`；时间档走 `dim_app_attribution_time_config` 的 **default** 四档（600/40、3600/30、21600/20、86400/10），新 app **不必单独插 time_config**
- 归因命中逻辑：IP + 24h 落地页主命中，设备四维 + 时间档加分，总分 ≥40 才 success

