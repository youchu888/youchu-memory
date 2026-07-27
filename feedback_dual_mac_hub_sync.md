# Feedback：双 Mac · 旧机主控 + 记忆/任务双向同步

**适用**：又初双 Mac（旧 Mac = 常驻主控，新 Mac = 编码/备份）

## 架构（主人 2026-07-27）

| 角色 | 机器 | 职责 |
|------|------|------|
| **主控 / 类服务器** | 旧 Mac（`old-mac`） | TG bot、agent-bus poller、接单干活；一般不断网 |
| **工作机** | 新 Mac（`new-mac`） | 可写代码、写 lesson/work-log；**不接实时 bot** |

## 同步什么 / 不同步什么

**双向同步（经 `youchu-memory` Git，约 10 分钟）**：

- lesson / feedback / MEMORY / sessions
- work-log（各机 `hosts/<id>/` → 合并稿）
- **ops-mirror**：近期 bus/任务溯源 + 未结案 bus 摘要（旧机权威写 `LATEST.md`）
- 群聊冷归档

**不同步（有意）**：

- TG 聊天原文、`tgbot.db`、Telethon session、`.env`
- agent-bus 完整 state（435MB+，且双机同时 poll 会抢单）

## 实时派单怎么走

1. 狂人/平台发 bus → **只旧 Mac poller 拉取并唤醒 Cursor**
2. 干完后：reply 结案 + 写 work-log / lesson
3. sync 后新 Mac 能看到：**做过什么、沉淀了什么、未结案摘要（LATEST）**
4. 新 Mac **不会**自动被同一条 bus 叫醒（正确；避免双机抢活）

## Agent 习惯

- 任一台收尾：写 `CHcode/.cursor/work-log/当日.md` + 该写的 lesson
- 读跨机任务：先看 `~/.dc-platform/memory/ops-mirror/LATEST.md` 与 `work-log/当日.md`
- 换到新 Mac **接单**：先停旧机 poller，再启新机（主控切换）；日常不要双开

## 脚本

- `bash ~/.dc-platform/scripts/sync-memory-git.sh`
- `python3 ~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py`
- `python3 ~/.dc-platform/memory/scripts/ops_mirror_to_memory.py`
