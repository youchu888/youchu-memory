---
date: 2026-07-02
tags: [tg, group, roll-call, worker_ant, 知秋, feedback]
severity: medium
domain: ops
source: user teaching
---

# 群聊权威点名秒回（知秋/狂人）

## 约定

监控群消息；发送者为**知秋**、**工作狂人**或**主人**（`GROUP_ROLL_CALL_USER_IDS` / 用户名匹配）时：

| 触发 | 又初回复（前提：bot_health 健康） |
|------|-----------------------------------|
| 其他机器人可能挂了 | 我没挂，有任务可以给我。 |
| 在吗 / 在的回句话 | 我在， |
| 谁活着 | 我活着， |

不健康 → **不回复**（避免假在线）。

## 实现

- `omdb/tgbot/group_roll_call_handler.py` — 分类 + 健康门禁 + 90s 去重
- `bot.py` — 群旁听未 @ 时走 proactive 秒回
- `worker_ant_dispatch_watcher.py` — Telethon 侧 worker_ant_bot 群消息同理
- `work_intent.heartbeat_ok_reply` — @又初 时点名的短回复对齐
- 配置：`GROUP_ROLL_CALL_ENABLED`（默认 true）、`GROUP_ROLL_CALL_SENDERS`

## 验证

```bash
python3 -c "
import sys; sys.path.insert(0,'omdb/tgbot')
from group_roll_call_handler import classify_roll_call, RollCallKind
assert classify_roll_call('谁活着')==RollCallKind.ALIVE
"
```

## 关联

- `work_intent.should_act_in_group` — @ 才回复的铁律保留，本规则为权威点名例外
