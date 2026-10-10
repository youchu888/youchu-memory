# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 10 2026 agent_session_rotate calendar | `~/.dc-platform/memory/lessons/2026-10-10-问-几点打卡-须先查当日-cn_punch_calendar-用北京时间报上下班计划-并分开说明.md` | 2026-10-10-问-几点打卡-须先查当日-cn_punch_calenda |
| jst 上下 下文 东京 东京时间 为准 | `sessions/tg-rotate-2026-10-10-0955.md` | 用户侧上下文若写 JST/东京时间，对外报打卡仍以**北京时间**为准，避免时区 |
| 09 50 52 不必 不必让用户立刻重复手打 会在 | `sessions/tg-rotate-2026-10-10-0955.md` | 若刚试过打卡但接口断开（如 09:50、09:52 连续失败），应说明失败原因  |
| 「卡 「计 」和 上」 上要 为已 | `sessions/tg-rotate-2026-10-10-0955.md` | 同时区分「计划打几点」和「卡是否已打上」；未打上要单独说明，避免用户以为已经打卡 |
| eh hr ne on 上班 下班 | `sessions/tg-rotate-2026-10-10-0955.md` | 标准答复：用**北京时间**给出**上班**、**下班**两个计划时刻（OneH |
| 「查 」流 一套 一定 上班 不打 | `sessions/tg-rotate-2026-10-10-0955.md` | 周六若有上班安排，仍走同一套「查日历 → 报计划 → 报实际/重试状态」流程，不 |
| should_skip_punch 「今 一致 上下 下班 不要 | `sessions/tg-rotate-2026-10-10-0955.md` | 与请假规则一致：若 `should_skip_punch` 为真，应明确「今日跳 |
| 「当 」日 不同 今日 值班 值班各自规则不同 | `sessions/tg-rotate-2026-10-10-0955.md` | 周六、法定假、请假、值班各自规则不同；回答前必须用「当天」日历判定是报时刻还是说 |
| 「几 」时 不要 不要按平日默认时间猜 与调 先查 | `sessions/tg-rotate-2026-10-10-0955.md` | 私聊问「几点打卡」时，先查当日打卡日历与调度计划，再回答，不要按平日默认时间猜。 |
| ## 09 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-09-问表-专项负责人时先查工作簿与需求-owner-再答-来源留存表-dws-dws_source_.md` | 2026-10-09-问表-专项负责人时先查工作簿与需求-owner-再答-来源 |
| memory_open pinned tags 业务 业务分工事实 为准 | `sessions/tg-rotate-2026-10-09-1045.md` | 冷启动仍按 PINNED / MEMORY_OPEN / 按任务 tags 深读 |
| owner 于口 人类 优于 优于口头记忆 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | 负责人类问题：工作簿条目名 + 表名/需求文档里的 owner 字段，优于口头记 |
| 「来 」挂 与留 交叉 作簿 分析 | `sessions/tg-rotate-2026-10-09-1045.md` | 当日工作簿里「来源分析验证数据」挂在野花名下，可与留存表归属交叉印证。 |
| 人同 侧登 同样 在需 存表 样是 | `sessions/tg-rotate-2026-10-09-1045.md` | 该留存表在需求侧登记的负责人同样是**野花**。 |
| 0留 15留 30 30留） 7留 dws.dws_source_analysi | `sessions/tg-rotate-2026-10-09-1045.md` | 来源分析留存指标落在表 `dws.dws_source_analysis_ret |
| 业务 业务负责人是 为准 人是 以工 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | **来源留存**业务负责人是**野花**（需求/验证口径以工作簿为准）。 |
| memory 「来 」时 不凭 不凭印象或 作簿 | `sessions/tg-rotate-2026-10-09-1045.md` | 问「来源留存谁负责」时，先对工作簿和近期分工核对，不凭印象或 MEMORY 猜负 |
| ho hot（须同时看「按时间最近动过」） ot t（ 「按 」） | `sessions/tg-rotate-2026-10-09-1045.md` | > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」 |
| ## 07 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-07-岗位用大数据-数仓白名单筛-勿用-negative-误杀分析师等混岗标题.md` | 2026-10-07-岗位用大数据-数仓白名单筛-勿用-negative-误杀分 |
| ## 07 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-10-07-第三国远程与到岗类一律不推-无需到岗-不拦-改-ethan_channel_bigdata_jo.md` | 2026-10-07-第三国远程与到岗类一律不推-无需到岗-不拦-改-ethan |
| ar dba flink pa rk sp | `sessions/tg-rotate-2026-10-07-2148.md` | 岗位：只要大数据开发 / 数据仓库开发及相关技术栈（Spark、Flink、数仓 |
| 「无 」不 不应 不应拦截 不算 到岗 | `sessions/tg-rotate-2026-10-07-2148.md` | 正文含「无需到岗」不算到岗，不应拦截 |
| #到岗 「到 「第 」及 」（ 三国 | `sessions/tg-rotate-2026-10-07-2148.md` | 地点：只推普通远程/居家；永久丢弃「第三国远程」及各类「到岗」（含 #到岗、需到 |
| .dc ethan ethan_channel_bigdata_jobs. et | `sessions/tg-rotate-2026-10-07-2148.md` | Ethan 岗位监控脚本：`omdb/tgbot/scripts/ethan_c |
| ethan jobs lesson negative watch 仓白 | `sessions/tg-rotate-2026-10-07-2148.md` | [LESSON: ethan-jobs-watch/岗位用大数据/数仓白名单筛， |
| 三国 不要 不要到岗 不要第三国远程 与数 仓开 | `sessions/tg-rotate-2026-10-07-2148.md` | 用户偏好已写入规则：不要第三国远程、不要到岗；岗位范围只要大数据开发与数仓开发相 |
| at dba eg e— ga iv | `sessions/tg-rotate-2026-10-07-2148.md` | 岗位过滤用白名单/正向关键词，不要把分析师、DBA 塞进 NEGATIVE——会 |
| —— —已 「仅 「到 「第 「远 | `sessions/tg-rotate-2026-10-07-2148.md` | 旧坑：曾把「第三国远程」当远程命中；正文同时有「远程」和「到岗」仍可能误推——已 |
| com.youchu.ethan jobs reload restart tg  | `sessions/tg-rotate-2026-10-07-2148.md` | 改过滤规则后必须 reload/restart `com.youchu.etha |
| ## 04 10 2026 agent agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-04-并行-lane-被长任务占用时-新私聊独立会话且须冷启动-连接失败勿依赖旧-resume-等网络.md` | 2026-10-04-并行-lane-被长任务占用时-新私聊独立会话且须冷启动- |
| ## 04 10 2026 ag agent_session_rotate | `~/.dc-platform/memory/lessons/2026-10-04-tg-cursor-连续-econnreset-或-api-不可达时-先排查-openvpn-代.md` | 2026-10-04-tg-cursor-连续-econnreset-或-api |
| agent api excerpt vpn 不在 不在复述错误栈原文 | `sessions/tg-rotate-2026-10-04-0648.md` | 此类 excerpt 蒸馏价值在**运维排障顺序**（关 VPN → 验 API |
| ag agent agent·并行」 en ge nt | `sessions/tg-rotate-2026-10-04-0648.md` | **并行 agent**：长任务占另一路时，新私聊走「新开 agent·并行」， |
| agent」 cursor resume 「重启 上下 下文 | `sessions/tg-rotate-2026-10-04-0648.md` | 「重启 agent」= 强制**新开** Cursor 会话；连接失败路径会** |
| api cursor failed https_proxy openvpn re | `sessions/tg-rotate-2026-10-04-0648.md` | 提示 `Failed to reach the Cursor API` 时，除代 |
| ap cursor econnreset pi read sql | `sessions/tg-rotate-2026-10-04-0648.md` | `read ECONNRESET` 表示与 Cursor 的会话连接被对端或中间 |
| cursor onehr tg 「已 「打 」属 | `sessions/tg-rotate-2026-10-04-0648.md` | TG 私聊「打卡了吗」属于考勤确认，正常应走 OneHR/打卡日历逻辑；本会话因 |
| agent lane lesson parallel resume tg | `sessions/tg-rotate-2026-10-04-0648.md` | [LESSON: tg-parallel-agent/并行 lane 被长任务占 |
| ag agent」仍报连接失败 en ge nt resume | `sessions/tg-rotate-2026-10-04-0648.md` | 用户连发两次「重启 agent」仍报连接失败 → 根因在**环境网络未恢复**（ |
| agent」 tg 「重 仍连 会话 假装 | `sessions/tg-rotate-2026-10-04-0648.md` | 连接失败后标准话术：请用户**重发刚才那句**，或再发「重启 agent」；勿在 |
