---
date: 2026-09-27
tags: [automation, launchd, tgbot, new-mac, TCC, Desktop]
severity: high
domain: ops
---

# 自动化迁 new-mac：tgbot 须 App Support runtime，禁 launchd 直读 Desktop

## 背景

old-mac 停用，权威机与 LaunchAgents 迁到 new-mac。项目在 `~/Desktop/CHcode`，launchd 的 bash **无 Desktop TCC**，直接跑仓内 `_env.sh` / `.venv` / `.env` 会 `Operation not permitted`，进而落到无 `telegram` 的系统 Python。

## 坑 / 错误做法

- 把仓内 `_env.sh` 原样 cp 到 App Support 再 kickstart（enable 脚本曾经这么干）
- 依赖 `Desktop/.../.venv/bin/python` 的 `[ -x ]` 探测（bash 测 Desktop 会失败）
- 双 label：`com.youchu.tgbot-dc` + `com.dc.tgbot-daemon` 互相重启

## 正确做法

1. `AUTHORITY_HOST=new-mac`，`WORKLOG_HOST_ID=new-mac`
2. 一键：`bash omdb/tgbot/deploy_app_support_runtime.sh`  
   - runtime + `.env` → `~/Library/Application Support/tgbot-dc/runtime`  
   - site-packages → `.../tgbot-dc/site-packages`  
   - 解释器用已授 Desktop TCC 的 Homebrew `python3.14`  
   - 单一 label：`com.dc.tgbot-daemon`
3. 总装：`bash .cursor/scripts/enable-automation-as-authority-new-mac.sh`（已改为调 deploy，不再盖坏 `_env`）
4. 旧机若仍开机：unload 同名 LaunchAgents 或关机，避免双 bot 抢轮询

## 验证

- `launchctl print gui/$(id -u)/com.dc.tgbot-daemon` 存在
- `daemon_check.sh` exit 0；`/tmp/tgbot-dc.heartbeat` 在更新
- 日志有 `Application started` / `getMe` 200
- 其它：agent-bus / vpn-sync / onehr / daily-report-* / memory-git-sync / ethan-jobs-watch 均为 OK

## 关联

- 脚本：`omdb/tgbot/deploy_app_support_runtime.sh`
- 脚本：`.cursor/scripts/enable-automation-as-authority-new-mac.sh`
- PINNED：日报推送权威机 = new-mac
