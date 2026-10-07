# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-07 · 最新归档：`sessions/tg-rotate-2026-10-07-2148.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 改过滤规则后必须 reload/restart `com.youchu.ethan-jobs-watch`，新 TG 消息才按新规则筛
- 旧坑：曾把「第三国远程」当远程命中；正文同时有「远程」和「到岗」仍可能误推——已改为简化拦截并在非「仅远程」模式也排除
- 岗位过滤用白名单/正向关键词，不要把分析师、DBA 塞进 NEGATIVE——会误杀「大数据开发 + 分析师」混岗帖
- 用户偏好已写入规则：不要第三国远程、不要到岗；岗位范围只要大数据开发与数仓开发相关
- [LESSON: ethan-jobs-watch|岗位用大数据/数仓白名单筛，勿用 NEGATIVE 误杀分析师等混岗标题]
- Ethan 岗位监控脚本：`omdb/tgbot/scripts/ethan_channel_bigdata_jobs.py`（常量区 + 文件头规则说明）；配套记忆：`~/.dc-platform/memory/feedback_ethan_jobs_filter.md`
- 地点：只推普通远程/居家；永久丢弃「第三国远程」及各类「到岗」（含 #到岗、需到岗、入职日/新/菲等）
- 正文含「无需到岗」不算到岗，不应拦截
- 岗位：只要大数据开发 / 数据仓库开发及相关技术栈（Spark、Flink、数仓等）；去掉纯数据分析师、DBA 向
- 主人明确说「先关闭 OpenVPN」时，应理解为：**先恢复 Cursor 可达性**，再处理原意图（打卡查询、重启 agent 等），顺序不要颠倒。
- 连接失败后标准话术：请用户**重发刚才那句**，或再发「重启 agent」；勿在 TG 里假装仍连着旧会话继续干。
- 用户连发两次「重启 agent」仍报连接失败 → 根因在**环境网络未恢复**（VPN/代理/防火墙），不是多重启几次 resume 能修好。
- [LESSON: tg-parallel-agent|并行 lane 被长任务占用时，新私聊独立会话且须冷启动；连接失败勿依赖旧 resume，等网络恢复后让用户重发原句]
- TG 私聊「打卡了吗」属于考勤确认，正常应走 OneHR/打卡日历逻辑；本会话因 Cursor 侧未连上，**没有形成有效答复**，不能当「已处理」。
- `read ECONNRESET` 表示与 Cursor 的会话连接被对端或中间网络重置，常与「API 不可达」同一类**网络/链路**问题，不是业务 SQL 类错误。
- 提示 `Failed to reach the Cursor API` 时，除代理（`HTTPS_PROXY`）外，还应看本机 **OpenVPN 是否改默认路由**、是否与 Cursor 出口冲突。
- 「重启 agent」= 强制**新开** Cursor 会话；连接失败路径会**自动丢弃旧 resume**，旧上下文不可继续用。
- **并行 agent**：长任务占另一路时，新私聊走「新开 agent·并行」，须**先冷启动读记忆**（bootstrap），不能假设与占线会话共享上下文。

