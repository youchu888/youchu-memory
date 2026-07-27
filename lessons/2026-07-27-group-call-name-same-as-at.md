---
date: 2026-07-27
tags: [tgbot, group, mention, 又初, 初儿]
severity: high
domain: ops
---

# 群聊点名：@机器人 / 喊又初·初儿 均须回复

## 规则（主人 2026-07-27）

**仅机器人群** `MONITOR_GROUP_CHAT_ID`（`-5376962870`）旁听仍开；**群里回复**触发任一即可：

1. `@youchu_ai_bot` / `@youchu8888` / `GROUP_REPLY_MENTIONS` / 主人账号 text_mention
2. 正文含「又初」「初儿」（及「给又初」等）
3. 回复本 bot 的消息

仅 `@mudan99_bot` 等其他 bot、未点名又初 → 旁听不回。

**抽查群** `ATTENDANCE_CHECK_CHAT_ID` 等不启用喊名扩展；抽查仍走 Telethon attendance，勿混进 bot 群规则。

## 实现

`_bot_was_addressed` 复用 `message_targets_youchu`；prompt/style 已改「喊名=@同效」。

## 验证

`初儿帮我看下` → 应进工作流；`@mudan99_bot 看下` → 不回。
