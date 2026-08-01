---
date: 2026-08-01
tags: [memory-git, dual-mac, new-mac, launchd, rebase]
severity: high
domain: ops
---

# 新 Mac memory 同步总失败：旧脚本无自愈 + work-log 合并稿易冲突

## 背景

新 Mac LaunchAgent 每 10 分钟跑 memory sync，长期 exit 2；日志反复卡在 `work-log/2026-07-28.md` rebase 冲突。

## 根因（叠在一起）

1. **LaunchAgent 跑的是旧脚本** `~/.dc-platform/scripts/sync-memory-git.sh`（07-24），冲突时只 `rebase --abort` + `exit 2`。
2. **仓内已有新脚本** `memory/scripts/sync-memory-git.sh`（07-28）带 `_heal_rebase_conflicts` / 失败则 `reset --hard origin` 兜底；旧脚本**没有**「CANON 更新则自覆盖」逻辑，所以永远升不上去。
3. **每轮先跑 `worklog_dual_mac_sync`**，重写合并稿时间戳并 commit；旧 Mac 也在推同一文件 → rebase 必撞；abort 后本地提交堆到 50+，下一轮更难。
4. 偶发 `ssh github.com:22 Connection refused` 加重分叉。

## 正确做法

1. 保证 `~/.dc-platform/scripts/sync-memory-git.sh` **等于**仓内 `memory/scripts/sync-memory-git.sh`（或改 plist 直指仓内脚本）。
2. 冲突雪崩时：救出本机独有 lesson → `reset --hard origin/main` → 补回再 push。
3. `.env.host` 固定 `WORKLOG_HOST_ID=new-mac`；正式日报权威仍是 `old-mac`。

## 验证

- `rg _heal_rebase ~/.dc-platform/scripts/sync-memory-git.sh` 能命中
- 手动 `bash ~/.dc-platform/scripts/sync-memory-git.sh` 打印 `OK memory 已同步`
- `launchctl print ... last exit code = 0`
