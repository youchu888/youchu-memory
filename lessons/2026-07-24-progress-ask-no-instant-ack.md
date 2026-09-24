---
date: 2026-07-24
tags: [tg, group, progress, instant-ack, self-evolve, feedback]
severity: high
domain: ops
---

# 群聊问进度禁止秒回「行，我来」罐头 ACK

## 背景

主人在群里 `@youchu_ai_bot 进度如何了`，初儿秒回「行，我来。」，被批评像轮询、看不出学习进化。

## 坑 / 错误做法

1. 「进度如何了」未命中 `direct_commands.parse` → 走普通派活路径
2. `_group_work_instant_ack` / `instant_group_ack` 从 `_INSTANT_ACK_DEFAULTS` 抽一句罐头确认
3. 真进度要等 Agent 慢回，首条观感 = 机械轮询

## 正确做法

1. `is_progress_ask(text)` 覆盖「进度/进展 + 如何了/怎么样」等口语；`parse` → `kind=progress`
2. `execute(progress)` 直出 `_build_progress_snapshot()`（busy / 记忆召回 / 今日实活），**不经 Agent**
3. 防御：`instant_group_ack` 对进度问返回空；`_group_work_instant_ack` 直接 `return None`

## 验证

```bash
cd omdb/tgbot
# tgreport env
python -c "from direct_commands import parse, is_progress_ask; from group_reply_style import instant_group_ack; t='进度如何了'; print(parse(t).kind, is_progress_ask(t), repr(instant_group_ack(t)))"
# 期望: progress True ''
bash omdb/tgbot/restart.sh
# 群里再 @ 问「进度如何了」→ 应直接短报，无「行，我来」
```

## 关联

- 脚本：`omdb/tgbot/direct_commands.py`、`group_reply_style.py`、`bot.py`
- 记忆召回：`omdb/tgbot/memory_recall.py`
