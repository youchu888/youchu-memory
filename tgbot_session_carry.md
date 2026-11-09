# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-10 · 最新归档：`sessions/tg-rotate-2026-11-10-0602.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 日报云端上传**：以已定稿 `reports/日报-YYYY-MM-DD.md` **原封不动**跑上传脚本；未说改字则不要改写后再传。
- [LESSON: agent-bus,tg|ack 若 `dropped=silent`，用 `--no-dedup` 或 progress 顶替，勿把未收到 ack 当已 ack。]
- **TG `status_mirror`**：狂人 bus 入站会先私聊 `🐜 狂人→又初`，ACK/结案后再 `📤 又初→狂人`；「只有我又初在回」常见是**旧单补结案**（入站超约 6h 且过 cutoff）**故意不重推狂人正文**，只推 outbound，不是链路坏了。
- **认 TG 标题**：🐜 = 狂人原文；📤 = 又初回执/结案；心跳 / lesson / 重唤醒默认不进 TG。
- **对单条 bus**：查 `incoming bus=<id> → TG` 日志；真人新单若已 mirroring 入站，私聊往上翻应对上 🐜 那条。
- **日报云端上传**：以已定稿 `reports/日报-YYYY-MM-DD.md` **原封不动**跑上传脚本；未说改字则不要改写后再传。
- **双机 memory 同步**：主人点名在 **old-mac** 跑 `bash ~/.dc-platform/scripts/sync-memory-git.sh`（导出当日 hosts work-log、rebase、推 youchu-memory `main`），常与日报收尾配套。
- **bus 派单 ACK**：`kind=ack` 可能被服务端 **`dropped=silent`**；秒回执被吞时用 **`--no-dedup` 重发 ack** 或先发 **progress** 顶住，再干活，最后 **reply** 才结案。
- **测试环境塌量（#12984）**：test SR `dw.dw_user_event_detail_new` 自 10-26/27 量级断崖；Paimon 同类与 `dws_settlement_detail` 分区明显滞后；先 **SR 核量** 再排 Flink/调度，**不碰 prod**。
- **测试机 SSH**：`root@43.213.29.105` 公钥未授权时 22 通但 **Permission denied**；跳板可达内网也不等于能上 YARN RM（8088 未必是 Hadoop-2 RM）；卡住时应 **请授权公钥** 再 SKIPPED/拉作业。
- **Spark 上产前 uid 字典号**：落表 **uid 类 bitmap** 才要 `impl=id_dict`（`mode=assign`、`kind=uid`、cand + `_uc`）；测试 `dict:uid_bl`，上产 `id_dict:uid`；怪 uid 不进；无号 `raise_error`；设备 bitmap 不动。
- **改前必核 DDL**：渠道日活、页面访问若仅为 **BIGINT 标量人数、无 uid bitmap**，人数与编码无关 → **无 bitmap，不改**；误加的取号步应撤回。
- **渠道指标日报**：落 **bm_union 原 uid** → 照旧样板改字典号并保留交付。
- **环境未恢复**：编排/SQL 可先推 `dev` commit，**单跑 cmp 交审**等测试集群/Flink 可用后再做。
- 群里 **禁止 @ 不在当前群成员**：先确认对方是否在群，再决定是否 @。
- Fanout / Flink 升级** 等需权限或 infra 介入的事项：走 **有权限的同事** 或 **agent-bus 派单**，不要在群里硬 @ 斯科特。
- 对末尾「当前问题」要 **直接答复**，不要只复述 prompt 全文。
- [LESSON: 群聊@ | 禁止 @ 不在当前群的人；斯科特不在群，Fanout/Flink 升级改走有权限的人或 bus，禁止群里 @斯科特]**

