---
date: 2026-08-31
tags: [tgbot, worker_ant, ux, session-rotate]
severity: low
domain: ops
---

# TG 问狂人超时勿标「狂人回复」

## 背景

私聊转问工作狂人，120s 内无实质回复时，出站标题仍显示「狂人回复」，与正文「已通过 agent-bus…等待 120s 内未收到实质回复」矛盾。

## 修复

- `worker_ant_bus.ask_outcome_title(reply)`：正文以「已通过 agent-bus 发给工作狂人」开头 → 标题「已转问狂人」；否则「狂人回复」
- `direct_commands._ask_worker_ant_direct` 使用该 helper

## 双机同步

`omdb/tgbot/` 不入 CHcode git → memory 补丁：

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_ask_outcome_title.sh
```

补丁目录：`patches/tgbot-ask-outcome-title/`（`direct_commands.py` + `worker_ant_bus.py`）

## 验证

```bash
python3 -c "
import sys; sys.path.insert(0,'omdb/tgbot')
from worker_ant_bus import ask_outcome_title
assert ask_outcome_title('已通过 agent-bus 发给工作狂人（bus id=1）。等待 120s…') == '已转问狂人'
"
```
