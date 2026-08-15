---
date: 2026-08-15
tags: [agent-bus, poller, launchd, robustness]
severity: high
domain: ops
---

# poller 遇 API 超时必须续心跳；启动脚本先写 pid 再 bootstrap

## 背景

2026-08-15 下午通道「半死」：TG bot 已恢复，但 agent-bus poller 对 `54.255.236.159:8012` 间歇 `urlopen timed out`。curl/peek 往往 0.5s 就通，inbox 偶发 30s 超时。

## 坑 / 错误做法

1. `poll_once` 成功才 `touch_poller_heartbeat`。连续两次 30s 超时 → 心跳超过 60s → daemon 当死进程杀掉重拉。
2. `start-agent-bus-poller.sh` 先跑三遍 `--once`（每次也可堵 30s）再 `nohup` 写 pid。空窗里 daemon 判定「进程不存在」，连环 `poller start`。
3. `agent_bus_health.py` 每次自检打 `fetch_inbox`（重），自己再堵 30s。
4. 写 lesson 说「已修好」但活代码没改（08-14 日报同构，禁止再犯）。

## 正确做法

1. 循环 `except` 里也 `touch_poller_heartbeat`（进程还活着）。
2. start 脚本：**先 nohup + 写 pidfile + 心跳**，再做 `--link/--init/--seal`。
3. 健康探针用 `peek`，不要每次拉 inbox。
4. 改完必须同步 `~/Library/Application Support/youchu-agent-bus/python/` 与 `scripts/`，以 pid/日志确认不是旧进程。

## 验证

`agent-bus-poller-check.sh` 为 OK；`poller.log` 允许偶发 timeout，但不应每 30s 一条 `poller start`。`peek has_new` 可用。

## 关联

- 脚本：`.claude/database/scripts/notify/agent_bus_poll.py`、`agent_bus_health.py`、`.cursor/scripts/start-agent-bus-poller.sh`
- 部署：`.cursor/scripts/sync-agent-bus-deploy.sh`
