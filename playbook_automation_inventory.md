# 自动化全景清单与优化方案（又初 · 2026-11-20）

> 权威机：**old-mac**（`AUTHORITY_HOST=old-mac`）  
> new-mac：`DISABLE_LOCAL_AUTOMATION` —— 不保活、不重装；可保留 memory 同步贡献 hosts  
> 原则：**主路径成功即停；失败才补一刀；改 A 不许伤 B**

---

## 0. 大局：三类自动化

| 类 | 含义 | 成员 |
|----|------|------|
| A 常驻保活 | KeepAlive / 进程必须在 | tgbot、agent-bus、onehr、ethan；外加 automation-ensure 巡检 |
| B 定时业务 | 到点做事一次 | 日报链、狂人学习、记忆日清、群学习、chcode 日同步、pre-flush |
| C 同步底座 | 双机/仓同步 | memory-git-sync（interval 或 daily）、vpn-sync |

改动顺序建议：**先 B（日报）→ 再 C（sync 节奏）→ 最后 A（保活间隔）**。同类一次只动一条链，留 1～2 天观察。

---

## 1. 清单（名字 / 何时 / 成功标记 / 失败才干什么）

### A. 常驻保活（权威机）

| 名字（LaunchAgent） | 何时跑 | 成功标记 | 失败才干什么 | 备注 |
|---------------------|--------|----------|--------------|------|
| `com.dc.tgbot-daemon` | 登录起 + KeepAlive | `/tmp/tgbot-dc.heartbeat` 新鲜（ensure 阈值 ~120s） | ensure 每 2 分钟发现无 PID 或心跳僵死 → kickstart | 私聊/群入口 |
| `com.youchu.agent-bus-poller` | 登录起 + KeepAlive | `…/youchu-agent-bus/state/youchu_ai_poller.heartbeat`（ensure >180s 告警并 kick） | 同上 | 派单收件；与 Cursor executor 联动 |
| `com.youchu.onehr-checkin` | 登录起 + KeepAlive | 调度进程在；窗口内打卡成功日志 | ensure 无 PID → kick | 随机窗打卡 |
| `com.youchu.ethan-jobs-watch` | 登录起 + KeepAlive | watch 进程在 | ensure 无 PID → kick | 招聘岗监控 |
| `com.youchu.automation-ensure` | **每 120s** + RunAtLoad | 日志 `OK ensure 全部在跑` | 缺 load / 无 PID → bootstrap / kick | **元保活**：盯上面四项 + 定时项已 load |

### B. 定时业务（权威机；周日多数跳过）

| 名字 | 何时跑 | 成功标记 | 失败才干什么 | 冗余点 |
|------|--------|----------|--------------|--------|
| `com.youchu.pre-daily-report-flush` | 工作日 **21:20** / 周六 **18:20** | hosts 当日流水写入 + memory sync 尝试 | work-log 空则从 ops-mirror 兜底写；sync 失败只 warn | 与 wake 内 sync 重叠 |
| `com.youchu.daily-report-wake` | 工作日 **21:30** / 周六 **18:30** | `reports/.daily_report_dm_posted.json` 含当日；或至少定稿文件存在 | 只写 wake_feed；**自己不推** | 依赖 Cursor 接住 |
| `com.youchu.daily-report-fallback` | 工作日 **21:45 + 22:00** / 周六 **18:45 + 19:00** | 同上 `posted` 标记 | 已推 → skip；有稿 → 直推；无稿 → `auto_draft`（含简写展开）再推 | **双时刻硬兜底**；易与 wake 双推（已靠 marker） |
| `com.youchu.memory-git-sync` | 配置：`MODE=interval` 时 **每 120s**；`daily` 时默认 **22:30** | git push OK / 锁释放；日志 `OK memory 已同步` | flock 互斥；rebase 冲突自愈；失败安全回退 origin | 双机高频时锁竞争多 |
| `com.youchu.worker-ant-daily-learn` | 工作日 **22:40** | `…/worker-ant-learn-bus-sent/{day}.sent` | 已 sent → skip；发 bus 失败打 FAILED | 靠 IDE 收回复写 session |
| `com.youchu.memory-daily-light-tidy` | 工作日 **22:50** | bootstrap 重生；日志 sizes / learn_session | 无学到的 session 只 WARN，不重发学习 | 依赖 22:40 已触发 |
| `com.youchu.chcode-git-sync` | 日 **08:30**（+ RunAtLoad） | pull 成功日志 | 冲突则 ERROR，不 force | 代码仓只拉 |
| `com.youchu.daily-group-learn` | 每天 **02:00** | 分类沉淀 + 私聊汇总（脚本侧） | 缺料则跳过/短报 | new-mac 上也曾 enabled，需确认权威唯一 |

### C. 同步 / 网络

| 名字 | 何时跑 | 成功标记 | 失败才干什么 |
|------|--------|----------|--------------|
| `com.youchu.vpn-sync` | 每 **1800s** + RunAtLoad | VPN 配置对齐 | 失败重试下次 interval |
| memory peer / 其它 oneshot | 按需 | — | upgrade_todesk / tg-learn-fuse 等 oneshot，不入日常主链 |

### 晚间权威机时间轴（当前）

```
21:20  pre-flush（冲 hosts）
21:30  wake → Cursor 写稿推 TG（理想）
21:45  fallback（没推才定稿/推）
22:00  fallback 再跑（没推才动）
22:30  memory sync（若 MODE=daily；interval 模式则全天 2min）
22:40  狂人学习 bus
22:50  记忆日清
```

---

## 2. 问题画像（为何显得冗余）

1. **成功定义不统一**：有的看 heartbeat、有的看 posted json、有的看 sent 文件、有的只看日志一行。  
2. **主路径与兜底职责粘连**：日报 wake 不推、fallback 又推两次；pre-flush 与 wake 都 sync。  
3. **元保活过勤**：ensure 每 2 分钟扫全表；memory interval 也 2 分钟 → 锁/日志/CPU 叠层。  
4. **双机历史**：权威来回切过；new-mac 禁用后旧 plist 堆在 `disabled-on-new-mac/`，易误判「本机还在跑」。  
5. **脚本双副本**：`.cursor/scripts`（gitignore）vs `Application Support` vs `memory/scripts` —— 改一处不同步。

---

## 3. 统一优化方案（健全优先，不许改崩旁路）

### 3.1 总原则

| # | 原则 |
|---|------|
| 1 | **一条链一个成功标记**（当日 key）；成功后同链后续时刻只 skip |
| 2 | **主路径优先，失败才兜底**；兜底最多一刀（不要 21:45+22:00 两刀） |
| 3 | **一次只改一条链**；改完权威机观察 ≥1 个完整工作日 |
| 4 | **仓内单源**：定时脚本进 `memory/scripts`（可 sync）；App Support 只做薄包装或安装时拷贝 |
| 5 | **旁路隔离**：改日报不得动 bus/打卡；改 sync 间隔不得动日报 marker |
| 6 | **回滚预案**：每个 LaunchAgent 保留旧 plist 备份文件名 `.bak-YYYYMMDD` |

### 3.2 分阶段（建议）

**阶段 0 · 只观测（0 改动）**  
在 old-mac 导出：`launchctl list | rg youchu` + 各 log 尾 50 行 + 标记文件是否当日命中。本清单对照打勾。

**阶段 1 · 日报链收口（优先，风险可控）**  
- 保留：21:30 wake（精品稿）  
- 兜底：**仅 21:45 一次**（已推 skip；未推 → auto_draft 展开简写 + 推）  
- 去掉：22:00 硬兜底；评估 21:20 pre-flush 是否并入 wake 开头（二选一，勿双 sync）  
- 验收：连续 2 个工作日 TG 恰一条；简写不进正文  

**阶段 2 · 晚间串行护栏**  
- 明确依赖：日报 posted →（可并行 sync）→ 22:40 学习 → 22:50 日清  
- 日清已有「学 session 可缺」WARN；勿让日清去重发学习 bus  

**阶段 3 · sync 节奏**  
- 权威机：评估 `MEMORY_SYNC_MODE=interval` 120s 是否可改为 **300～600s** 或「工作时段 interval + 晚间 daily」  
- new-mac：继续只 sync、不 ensure  
- 验收：锁竞争下降；hosts 仍当日可达  

**阶段 4 · 保活**  
- ensure 间隔 120s → **300s**（先改配置，不改判定逻辑）  
- heartbeat 阈值与 kick 阈值对齐  
- 验收：tgbot/bus 僵死仍能拉起；误 kick 不增加  

**阶段 5 · 单源安装**  
- install 脚本统一从 `memory/scripts` 拷到 App Support  
- 文档化：权威机安装手册一页  

### 3.3 明确「先别动」

- agent-bus / tgbot KeepAlive 逻辑（除非心跳误报）  
- onehr 随机窗  
- 云端上传（仍人工「上传云端」）  
- PINNED / 业务 ETL  

### 3.4 一页验收板（每阶段通用）

```
[ ] 权威机仍是 old-mac
[ ] new-mac DISABLE 仍在
[ ] 目标链成功标记当日命中
[ ] 旁路链（bus/打卡/tg）心跳正常
[ ] 无双推 / 无重复 bus 学习
[ ] 出问题：launchctl 回挂 .bak plist + kick
```

---

## 4. 变更记录

| 日期 | 说明 |
|------|------|
| 2026-11-20 | 初版全景：基于 new-mac disabled 镜像 plist + 仓内 install 脚本梳理；待 old-mac 实机核对补洞 |
