# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-11-28 · 最新归档：`sessions/tg-rotate-2026-11-28-0833.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 运维 DDL 统一发「大数据运维」群（chat_id `-5031650278`），用 `@wangyi00001` 点名执行；禁止只发仓库/本地路径（对方收不到）。
- 组合语句（如 `DROP`+`CREATE`）：打成一个文件整包发出，不要拆成两条消息。
- 等王毅回执续跑时：单独 agent/process 只读轮询 `group_raw`，不要用 tgbot 的 Telethon 会话，以免占住 Bot 收其他任务。
- [LESSON: 协作DDL交付|运维 DDL 发 chat_id=-5031650278；禁路径；单条 CREATE/ALTER 可贴 SQL 或单文件，组合 DROP+CREATE 打一份可打开文件（优先 .txt）；真人号 Telethon 发送；@wangyi00001 只写生产/测试+执行、SQL 少注释；续跑用独立进程盯 group_raw，不占 tgbot Telethon]**
- 单条 `CREATE` 或单条 `ALTER`：可把 SQL 直接贴在群里；单条 `CREATE` 也可发文件并 @王毅。
- 发文件前核对内容与可打开性；群里 `.sql` 有时打不开，组合脚本优先 `.txt`。
- tgbot（Bot）不在该群时 `getChat` 会 400；发运维群 DDL 走真人号 Telethon，不走 Bot API。
- 派单文案极简：`@wangyi00001` +「生产/测试」+「执行下」+ 正文；不写长解释旁白。
- 给王毅的脚本文件少注释，正文以可执行 SQL 为主。
- `group_raw` 旁听对「文档类/文件消息」可能漏记；监控要设合理 baseline（例如锚到已知文本消息），并以群内文字回复为触发核验的条件。
- 主人删消息重发时：先停旧监控进程，重发后再起新监控，避免双盯或盯错 msg id。
- 王毅跑完后用 prod 只读核列等后续，与「发 DDL」步骤分离。
- 实活必须先落本机 **`.cursor/work-log/当日.md`**；否则 flush/同步只能搬走空壳，双机合并稿也会缺 new-mac 内容（Cursor transcript 不跨机）。
- [LESSON: daily-report,new-mac,automation|关 new-mac 本地权威自动化时，必须保留 pre-daily-report-flush 与 memory-git-sync，否则双机 work-log 断流。]
- 日报链路已定：**21:20（周六 18:20）** 双机 `pre-daily-report-flush` 把当日流水 → `hosts` → `memory-git` 互相同步；**21:30（周六 18:30）** 仅 **old-mac** 合并 hosts、定稿、推 TG。
- 双机全天跑 **memory-git-sync**（约 **120s** 一轮），与定点 flush 并行，不靠单点手动拉。
- **定稿权威仍是 old-mac**；new-mac 设 `WORKLOG_HOST_ID=new-mac`，只负责本机 hosts 导出，不当 TG 推稿主机。
- new-mac 已恢复 **`com.youchu.pre-daily-report-flush`** 与 memory-git-sync；冲刺自检 **`biz=4;thin=0`** 且 hosts 可写才算过关。

