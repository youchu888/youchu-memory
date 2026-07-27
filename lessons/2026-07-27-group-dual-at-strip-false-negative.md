---
date: 2026-07-27
tags: [tgbot, group, mention, strip, session-rotate]
severity: high
domain: ops
---

# 群聊双 @ 勿因 strip @youchu 误判「没@初儿」

## 背景

群聊#146：知秋 `@youchu_ai_bot @mudan99_bot` 问口径。秒回 ACK 后，Agent 却回「没@初儿，群里不回」。

## 根因

`_bot_was_addressed` 用 Telegram entities 判定已 @ → 正确进工作流；  
但 `_strip_bot_mention` 把 `@youchu_ai_bot` 从正文剥掉再喂 Agent → 模型只看见 `@mudan99_bot` → 误判。

## 正确做法

1. 旁听/溯源归档保留**原文**（含 @）
2. 已判定 mentioned 时，Agent 输入加硬规则：「已 @ 初儿，禁止说群里不回」
3. 没 @ 本 bot 的消息：直接不回，别在群里解释为什么不回

## 验证

同时 @ youchu + mudan 的群问，应实质作答，不再出现「没@初儿」。

## 关联

- `omdb/tgbot/bot.py`（`_strip_bot_mention` + handle_message）
- `group_reply_style.py`
