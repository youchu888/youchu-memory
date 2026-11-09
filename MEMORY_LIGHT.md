# 记忆轻量读法（又初开工卡）

> **定案**：本来就是**索引制**，不是每次整库灌。繁重来自「没按索引读」+ 「bootstrap 里塞了不相关的 bus 积压」。  
> 路径：`~/.dc-platform/memory/`

## 三层（只认这三层）

| 层 | 文件 | 何时读 | 体积 |
|----|------|--------|------|
| **启动** | `.cursor/.agent-memory-bootstrap.md` | 新对话第一下 | 目标 ≪100KB；只含 OPEN + 最近动过 + 检索捷径（**不**灌红线全文） |
| **索引** | `lessons/_index.md` · `MEMORY.md` | **只 rg / 扫标题行**，不整篇 Read | 索引而已 |
| **原文** | 命中的 1～2 个 `lessons/` 或 `feedback_*` | 任务 tags 对上才读 | 按需 |

## 开工 30 秒流程（强制）

1. **Read bootstrap**（整份即可；别再平行 Read PINNED/OPEN/MEMORY）
2. 看用户任务 → 定 **1～2 个 tag**（如 `日报` / `vpn` / `渠道` / `dolphin`）
3. **`rg tag lessons/_index.md`** 或 MCP `memory_list` → 命中后 **只 `memory_read` 那 1～2 个文件**
4. 干完再写：优先 **update 旧 feedback/lesson**，少新建；新红线只追加 `pinned/*.md`（31+），**禁止**顶换 `PINNED.md` 1–30

## 禁止（这就是「梳理好久」的原因）

- ❌ 整篇 Read `MEMORY.md`（71KB 索引）
- ❌ 整篇 Read `lessons/_index.md`（300+ 行）
- ❌ 未定任务 tags 就扫一周 transcript
- ❌ 每个反馈都新建 lesson（同主题 update 旧条）
- ❌ 非 bus 任务还去啃 bootstrap §0.5 那堆历史未结案

## 任务 → tags 速查

| 活 | tags / 入口 |
|----|-------------|
| 日报/周报 | `日报` → `feedback_daily_report*` · `daily-report.mdc` |
| VPN | `vpn` → `vpn_ovpn_sync*` |
| 群进展/工作簿 | `workbook` → `workbook-tasks.mdc` · `project_youchu_workbook_tasks.md` |
| 海豚/补数 | `dolphin` `complement` |
| 上产 / fanout / `_r` bucket | `bucket` `prod` → `lookup-rules.sh bucket`（#33） |
| Spark 提审 / S7 / 影子产发 | `spark` `stage7` `request-publish` → **`playbook_spark_prod_publish.md`**（总册） |
| 核查 | `datacheck` → playbook 目录 |
| 归因 | `attribution` |
| 迁机/LaunchAgent | `new-mac` `launchd` `automation` |

## 晚间自主学习闭环（权威机 new-mac · 工作日）

| 时刻 | 动作 | 目的 |
|------|------|------|
| 21:30 / 21:45 | 日报 | 业务交付，不写运维 |
| 22:30 | memory git sync | 双机记忆对齐 |
| 09:00 | 向狂人学习（bus） | 工作日；假日/请假跳过；新知识进 `worker_ant/sessions/` → lesson |
| **22:50** | **记忆日清** `memory-daily-light-tidy.sh` | 重生 bootstrap、压 OPEN/PINNED 报警、保持次日轻启动 |
| **02:00** | **TG 回拉 + 学习 + 融合** `daily_group_chat_learn` → `memory-fuse-after-tg-learn.sh` | 闲聊丢弃；有用内容优先并入已有 lesson/feedback/settled；新建封顶；reference 去重 |

原则：**越学越快**——纠正 → update 旧 feedback/lesson（少新建）→ 红线首页冻结、续篇 append → 次日只啃 bootstrap + 按 tag `lookup-rules.sh`。  
TG 线铁律：**拉完就融合，不叠废话**；同义句已在记忆里 → 跳过新建。

```bash
bash ~/.dc-platform/scripts/memory-daily-light-tidy.sh          # 手动日清
bash .cursor/scripts/install-memory-daily-light-tidy-launchd.sh # 装 22:50
bash ~/.dc-platform/scripts/memory-fuse-after-tg-learn.sh --day YYYY-MM-DD  # TG 学后融合
bash /Users/mac/Desktop/CHcode/omdb/tgbot/scripts/install_daily_group_learn_launchd.sh  # 装 02:00
```
