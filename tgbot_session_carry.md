# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-31 · 最新归档：`sessions/tg-rotate-2026-10-31-0659.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 私聊「日报今日结果再加点内容」= 在**已定稿**上增补【今日结果】，不是从零写日报；先对齐当日真实交付再动笔。
- 增补前仍要**双机 work-log 同步**（或等价 `prepare_daily_report_sync`），用合并稿 + transcript/派单挖**当天实活**，禁止为凑条数硬拆或编造。
- 改定稿后**立刻重推 TG 私聊**（old-mac `post_daily_report_to_dm.py`）；对话里只确认「已推 + 稿路径」，**不要再贴全文**（防双推）。
- 大型 `tgbot/prompt_*.md`：先读启动包，再**读头尾**定位「当前问题」，不必通读全文。
- 补条与原有结果**并存**：保留已写实的交付（如渠道观影产发），只加漏记项（如上午渠道漏斗列数告警排查及与观影四表 SQL 同步收口）。
- 定稿路径：`.cursor/work-log/reports/日报-YYYY-MM-DD.md`，并**对齐 memory 镜像稿**（`work-log/reports/`）。
- 主人未说「上传云端」时：**只改本地 + TG**，不自动跑云端上传脚本。
- 收尾对用户：一句结果向（例：双机同步与 TG 重推成功、多补了哪一条业务说法），不必展开「无需后续」类套话。
- 主人问「各项进程是否正常」时，必须先读启动包与 TG prompt 文件，直接回答文件末尾「当前问题」，禁止只复述文件或空答。
- 健康检查应实查：`tgbot-daemon`、agent-bus（poller / wake-bridge / 未结案 bus）、OneHR 打卡、OpenVPN、在线保活（如 `tg-work-online`）、岗位监控、`away-health` 等综合结论。
- agent-bus 正常信号：poller 心跳约 1s、未结案 bus=0；若 away-health 刚自愈过 poller，应在结论里说明「现已稳」。
- launchd 类任务（日报 flush/wake、`vpn-sync`、memory-sync 等）「已加载」即可；空闲时无常驻 PID 属于正常现象，勿误判为挂了。
- 若数据侧有挂账，结论写「本机进程正常」后，可一句带过业务侧问题并问是否要追那条挂账现状。
- [LESSON: tg-prompt|超大 TG prompt 先读头尾定位「当前问题」，再实查作答，禁止空答与全文复读]**
- 超大 prompt 可先读头尾定位「当前问题」，再按需补读中间段，避免整文件加载拖慢响应。
- 回复宜用表格列出关键项：进程名、是否在跑、pid/心跳、当日打卡是否成功、VPN 是否已连及续期剩余时间。
- `away-health` 自检串（如 `OK bot+daemon+bus+vpn+caps+executor`）可作为本机运维面的一行总评，与分项表格互补。
- **产线数据告警**（如 pipeline-runner、剧集日表回写挂账）与 **本机 daemon/调度进程** 要分栏说明，避免主人以为 Bot/VPN/打卡挂了。

