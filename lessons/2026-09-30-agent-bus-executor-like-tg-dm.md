---
date: 2026-09-30
tags: [agent-bus, cursor-executor, tgbot]
severity: high
domain: ops
---

# agent-bus 与 TG 私聊同路：另起 headless 执行

## 背景

只靠 IDE 主会话接 wake 时，忙别的活会把 bus 晾在「处理中」（如 #9470）。主人定：收到的 bus 都要处理，另起执行。

## 正确做法

- `AGENT_BUS_CURSOR_AUTO_EXECUTE=true`
- `AGENT_BUS_IDE_WAKE_MODE=false`
- 配置：`~/Library/Application Support/youchu-agent-bus/config/agent-bus.env`
- `sync-agent-bus-deploy.sh` 不得写回 false
- 启动脚本 PATH 须含 `~/.local/bin`（`agent` CLI）

## 验证

```bash
cat ~/Library/Application\ Support/youchu-agent-bus/config/agent-bus.env
kill -0 "$(cat ~/Library/Application\ Support/youchu-agent-bus/state/cursor-executor.pid)"
tail -5 ~/Library/Application\ Support/youchu-agent-bus/state/cursor_executor.log
```

## 关联

- feedback_agent_bus_all_inbound_must_process.md
- TG Bot：`mode=Cursor Agent API`
