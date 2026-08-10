---
date: 2026-08-10
tags: [daily-report, launchd, tg, wake]
severity: high
domain: ops
---

# 日报 21:30 必须有 launchd 唤醒，不能只靠规则字面

## 背景

主人 21:40 追问为何没按 21:30 推 TG 日报。规则写了 `AGENT_LOOP_WAKE_DAILY_REPORT`，但本机无定时任务发出该哨兵，reminders 表也空。

## 正确做法

1. old-mac 安装：`bash .cursor/scripts/install-daily-report-wake-launchd.sh`
2. 21:30 脚本写 `wake_feed` 哨兵 + 先跑 `prepare_daily_report_sync`
3. 主会话接住后写日报并 `post_daily_report_to_dm.py`
4. 已推送日不重复唤醒

## 验证

`launchctl print gui/$UID/com.youchu.daily-report-wake` 可见；次日 21:30 有 `daily-report-wake.log`。
