---
date: 2026-09-29
tags: [worker-ant, learn, bus, launchd]
severity: high
domain: ops
---

# 每日学习必须自动发 bus，不能只写 wake_feed

## 背景

2026-09-28 22:40 wake 已写入，但 Cursor 未接住 → 未 `send → worker_ant`，主人侧无学习消息。

## 正确做法

`worker-ant-daily-learn-wake.sh`：先 `agent_bus_send.py --to worker_ant`（设 `DC_PLATFORM_JSON`），再写 wake 供 IDE 沉淀回复。marker：`state/worker-ant-learn-bus-sent/YYYY-MM-DD.sent`。

**禁止** `--kind progress`：那是已有线程的「阶段同步」。新提问用默认 kind（reply/message），TG 镜像才会按出站模板带 `出站 bus#id`。2026-09-29 补发 #9391 因 catchup 用了 progress，镜像只显示「阶段同步」、runtime 旧版还不展示 outbound_id。

## 验证

```bash
tail -20 "$HOME/Library/Application Support/youchu-agent-bus/state/worker-ant-learn-wake.log"
# 应见 send bus → worker_ant … bus sent OK id=…
```
