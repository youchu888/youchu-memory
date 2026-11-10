# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-11 · 最新归档：`sessions/tg-rotate-2026-11-11-0603.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- TG 超长 prompt（如 `prompt_*.md`）先读开头指令与末尾「当前问题」，按问题执行，勿复述全文。
- testcluster SSH 本机安装：`export GIT_SSH_BUNDLE_PASS="$(cat ~/.dc-platform/config/git-ssh-bundle.pass)"` 后跑 `bootstrap/testcluster-ssh/install-on-host.sh`（路径相对 memory 仓）。
- 登录默认是 `bigdata-dev`；要跑 Hadoop/集群侧命令用 `sudo -iu hadoop`，勿在 dev 用户下硬跑 hadoop 命令。
- 双机记忆同步固定起手：`cd ~/.dc-platform/memory && git pull --rebase`；已是最新即可收工，不必强推。
- 安装脚本会写入 `Host dolphinscheduler-2` 与私钥 `~/.ssh/id_ed25519_testcluster`；装完再验连，不单信脚本 exit 0。
- 连海豚/集群节点需先 VPN；验通用 `ssh dolphinscheduler-2 'hostname; whoami'`。
- 验通期望：`hostname` → `dolphinscheduler-2`，`whoami` → `bigdata-dev`；两字段对即算连通 OK。
- 私聊派活「同步记忆 + 装 SSH + 验 dolphin」可收成三步清单汇报：memory pull → install-on-host → ssh 两字段验证。
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

