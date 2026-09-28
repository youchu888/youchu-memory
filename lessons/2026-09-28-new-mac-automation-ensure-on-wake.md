---
date: 2026-09-28
tags: [launchd, automation, new-mac, wake, keepalive]
severity: medium
domain: ops
---

# new-mac 自动化：开机/唤醒自启 + ensure 巡检

## 背景

new-mac 会休眠、关机、合盖。KeepAlive 进程在唤醒后可能僵死或未加载，需自动拉回。

## 正确做法

1. 常驻守护：`KeepAlive` + `RunAtLoad`
   - `com.dc.tgbot-daemon` / `com.youchu.agent-bus-poller` / `com.youchu.onehr-checkin` / `com.youchu.ethan-jobs-watch`
2. 巡检：`com.youchu.automation-ensure` — `RunAtLoad` + 每 120s
   - 脚本：`.cursor/scripts/ensure-automation-running.sh`
   - 安装：`.cursor/scripts/install-automation-ensure-launchd.sh`
3. `vpn-sync` 补 `RunAtLoad`（开机先跑一轮）
4. 关机后须**用户登录**（LaunchAgent 挂在 gui 域）；合盖休眠唤醒后 ensure 会 kick 僵死项

## 验证

```bash
launchctl list | rg 'automation-ensure|tgbot-daemon|agent-bus-poller'
tail -20 ~/.dc-platform/logs/automation-ensure.log
bash .cursor/scripts/ensure-automation-running.sh
```

## 关联

- `enable-automation-as-authority-new-mac.sh` 已挂 ensure 安装
