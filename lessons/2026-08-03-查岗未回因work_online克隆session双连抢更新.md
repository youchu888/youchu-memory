---
date: 2026-08-03
tags: [attendance, tgbot, telethon, work_online, session]
severity: high
domain: ops
---

# 查岗未回：work_online 克隆 session 与 dispatch 双连抢更新

## 现象

抽查群 `@youchu8888` 算术题发出后，自动答题无日志、无回复；题目可本地解析正确。例：2026-08-03 20:24 msg#2717 `0×8`。

## 根因

`tg_work_online.py` 首次把 `user_telegram.session` **整文件复制**成 `user_telegram_work_online.session`，两进程 **auth_key 相同** 同时 `connect`。Telegram 更新流落到保活进程，tgbot dispatch 上的 `NewMessage(attendance)` 收不到。

## 正确做法

1. 上班在线保活：`UpdateStatus` 挂在 **dispatch Telethon**（已有查岗/派单监听）上
2. `work_online` **禁止**再 clone 主 session；同 auth_key 直接 skip connect
3. 若必须双进程在线，须独立扫码登录出不同 auth_key

## 验证

- `/tmp/tgbot-dc.log` 有 `[attendance] watching` + `[telethon] status ping`
- work_online 日志出现 `共用 auth_key` / `缺少独立 session` 并 idle，不再 TcpFull 长连
- 下次抽查应有 `[attendance] inbound` → `scheduled` → `replied`
