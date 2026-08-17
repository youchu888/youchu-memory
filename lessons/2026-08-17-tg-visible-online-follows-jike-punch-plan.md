---
date: 2026-08-17
tags: [tg, telethon, jike, punch, online]
severity: medium
domain: ops
---

# TG 绿点跟当天极客随机打卡计划走，TCP 不随下线断开

## 背景

打卡在窗内随机一刻（签到 09:30–10:00，签退 22:00–22:30 / 周六 19:00–19:30）。绿点原先写死 09:30–22:30，会早亮、晚灭，周六签退后还能绿到晚上。

## 坑 / 错误做法

- `UpdateStatus(offline=False)` 只要 Telethon 连着就刷 → 别人看到全天绿。
- 用断 TCP 来下线 → 查岗 / 派单监听一起没了；打卡也发不出去。
- `tg_work_online` 再 clone 主 session 双连 → 抽查收不到（见 2026-08-03）。

## 正确做法

- TCP 照常挂（dispatch Telethon）。
- 绿点读 `jike_checkin_state.json` 当天 `checkin_plan` / `checkout_plan`，已签退则灭。
- 签到/签退成功立刻 `apply_visible_online`，不等 45s ping。
- 改完只重启 `com.dc.tgbot-daemon`（`bash omdb/tgbot/restart.sh`），不动 VPN。

## 验证

- 已签退：`should_appear_online()` 为 False；日志 `visible online=False`。
- 次日：绿点应在当天随机签到计划附近亮，签退计划附近灭。

## 关联

- `omdb/tgbot/jike_checkin_watcher.py` `should_appear_online`
- `omdb/tgbot/worker_ant_dispatch_watcher.py` `apply_visible_online`
