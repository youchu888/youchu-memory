---
date: 2026-09-29
tags: [memory, learn, hygiene, light, new-mac]
severity: high
domain: ops
---

# 晚间闭环：狂人学习 → 记忆日清 → 次日轻启动

## 目标

越学越快越准。用现有记忆库，不另起炉灶。

## 闭环（权威机 new-mac · 工作日）

| 时刻 | 动作 |
|------|------|
| 22:40 | `worker-ant-daily-learn` → bus 提问 |
| 22:50 | `memory-daily-light-tidy` → 重生 bootstrap、OPEN/PINNED 体检 |

沉淀优先 update 旧条。卡：`MEMORY_LIGHT.md`。

## 命令

```bash
bash .cursor/scripts/install-memory-daily-light-tidy-launchd.sh
bash ~/.dc-platform/scripts/memory-daily-light-tidy.sh
```
