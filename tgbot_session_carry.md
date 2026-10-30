# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-10-30 · 最新归档：`sessions/tg-rotate-2026-10-30-1659.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

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
- 私聊编号（如 #591）可在对内归档时用；对外答复以实查结果和业务语义为主。
- 空输出 vs 额度**：`model=auto empty output`、多档模型连试仍无有效输出，优先查本机 Agent 鉴权/模型名/进程异常，不要默认等同网页用量面板耗尽。
- TG prompt 文件**：须冷启动读 bootstrap，再读指定 `prompt_*.md`；体量大时读**开头指令 + 末尾「当前问题」**，直接答末尾，禁止只复述文件或只报「正在读」。
- 用户问打卡异常**：走 OneHR/日历/launchd 与 `set_leave_day`/`set_duty_day` 等既有脚本与规则，禁止用模型故障话术搪塞。
- 积压问答标准答法**：先核 agent-bus 未结案数 + 私聊「未实质答复」清单（编号、原问、是否需补办），再结论；#588 类「唯一该补办」要显式点出。
- [LESSON: punch-attendance|用户问「打卡一直出问题」必须查打卡链路与最近失败原因，禁止只回模型额度或 empty output 模板]
- [LESSON: tgbot-prompt|执行 `/var/.../prompt_*.md` 时读头尾答「当前问题」；大文件禁止只复述、禁止用额度文案代替末尾问题的真实答案]
- **假「额度用尽」**：用户问打卡/积压等实活时，若未查库、未跑脚本就回模型 fallback 文案，等于未办结；该文案不能替代任务交付。

