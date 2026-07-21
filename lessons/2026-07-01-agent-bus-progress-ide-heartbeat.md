---
date: 2026-07-01
tags: [agent-bus, progress, tg, cursor, worker_ant]
severity: high
domain: ops
trigger: 等待执行, bus进度, status_mirror, IDE主会话
---

# agent-bus「等待执行」误报与 IDE 主会话盲区

## 背景

bus#652 已 ACK，TG 显示「已 ACK · 执行中」但信号为「等待执行」，并持续重唤醒 + progress 刷屏。

## 坑

1. **架构盲区**：派单在 **Cursor IDE 主会话**（wake_feed）执行；`agent_bus_progress.py` 只检测 `pgrep cursor-agent`（TG 拉起的 CLI）→ 两边都空闲时兜底文案 **「等待执行」**。
2. **未正式结案**：有 ACK、有 progress/reply 正文，但 `youchu_ai_sent.json` 缺 `reply:bus:N` 键（仅 `reply:fp:...`）→ poller 认为未结案，反复 rewake。
3. **双跑风险**：TG `full` 模式会 spawn cursor-agent，与 IDE 主会话重复干活。

## 正确做法

1. **进度信号**：ACK 后 `touch_ide_heartbeat(agent, bus_id)`；progress 检测 IDE heartbeat + `tg_agent_busy` 标志，不单盯 CLI。
2. **结案**：`agent_bus_send.py --kind reply --reply-to-bus-id N` 成功 → 写 `reply:bus:N` + `mark_processed`。
3. **重唤醒**：`bus_is_closed` / `should_skip_rewake` 在 agent busy 或已结案时跳过。
4. **模式**：`AGENT_BUS_TG_MODE=status_mirror`；派单由 IDE 主会话执行，TG 只镜像状态。
5. **自检**：`AGENT_BUS_STATE_DIR=... .cursor/scripts/agent-bus-poller-check.sh`

## 验证

- 结案后 `has_reply('youchu_ai', N)` 为 true，`reply:bus:N` 在 sent.json。
- progress 文案含「IDE 主会话」或 heartbeat 提示，而非长期「等待执行」。
- 已结案 bus 不再出现在 pending rewake。

## 关联

- 代码：`omdb/tgbot/agent_bus_progress.py`；`~/Library/Application Support/youchu-agent-bus/python/agent_bus_state.py`
- 规则：`.cursor/rules/agent-bus-session.mdc`
- 索引归档：`sessions/2026-07-01-attribution-p0-daily-archive.md`
