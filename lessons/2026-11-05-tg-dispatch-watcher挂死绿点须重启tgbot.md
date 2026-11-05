---
date: 2026-11-05
tags: [tg, telethon, visible-online, dispatch, keepalive, tgbot]
severity: high
domain: ops
---

# TG dispatch watcher 挂死 → 绿点断 · 须重启 tgbot（私聊#603）

## 背景

2026-11-05 问「tg保活的进程挂了？」：独立 launchd `com.youchu.tg-work-online` 仍在跑，但 `.env` `TG_WORK_ONLINE_ENABLED=false`（自 10-17 idle），**不是**现网绿点路径。现网靠 tgbot 内 **dispatch Telethon + visible-online**。

## 坑 / 错误做法

- 只看 `tg-work-online` pid 在跑就报「没挂」
- 不查 `[visible-online]` / `[dispatch] watcher` 当日日志
- 绿点断了只改打卡日历、不重启把 watcher 拉起

## 正确做法

1. 区分两路：独立保活（常禁用）vs **tgbot dispatch watcher**（现网）
2. 症状：Telethon 解析层报错（如 `Constructor ID 7600b9d3`）→ `[dispatch] watcher 异常退出` → 之后无 `[visible-online]`
3. 恢复：主人说「重启」后 `bash omdb/tgbot/restart.sh`（或等价），确认新 pid 后有间歇 `[visible-online]`
4. 判在线策略仍跟 OneHR 打卡（见既有 visible-online lesson）；本条只管 **watcher 死链**

## 验证

```bash
# 当日应有 visible-online；无则查最近 watcher 退出栈
rg -n "visible-online|watcher 异常|Constructor ID" "$(ls -t ~/Library/Logs/tgbot* 2>/dev/null | head -1)" 2>/dev/null | tail -20
launchctl print gui/$(id -u)/com.dc.tgbot-daemon 2>/dev/null | head -5
```

## 关联

- 私聊#603/#604/#605；进程 `com.dc.tgbot-daemon`
- 既有：`2026-09-28-tg-visible-online-follows-onehr-punch.md`
- 代码：`omdb/tgbot/worker_ant_dispatch_watcher.py` · `tg_visible_online.py`
