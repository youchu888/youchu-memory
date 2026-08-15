---
date: 2026-08-15
tags: [daily-report, launchd, schedule]
severity: high
domain: ops
---

# 日报推送：周六 18:30，其余工作日 21:30

## 背景

主人 2026-08-15 约定：周六提前推日报，周一至周五仍 21:30。周日不推。

## 坑 / 错误做法

只改规则字面、不重装 launchd，周六仍会等到 21:30。新机若不重装 flush，周六 18:30 可能缺 `hosts/new-mac`。

## 正确做法

整条链路一起前移（冲刺 −10 分钟，兜底 +15 分钟）：

| 日 | flush（双机） | wake（old-mac） | fallback（old-mac） |
|----|---------------|-----------------|---------------------|
| 周一至周五 | 21:20 | 21:30 | 21:45 |
| 周六 | 18:20 | 18:30 | 18:45 |
| 周日 | 跳过 | 跳过 | 跳过 |

```bash
# 两台都跑
bash ~/.dc-platform/memory/scripts/install-pre-daily-report-flush-launchd.sh
# 仅 old-mac
bash /Users/mac/Desktop/CHcode/.cursor/scripts/install-daily-report-wake-launchd.sh
bash /Users/mac/Desktop/CHcode/.cursor/scripts/install-daily-report-fallback-launchd.sh
```

## 验证

`launchctl print gui/$UID/com.youchu.daily-report-wake` 的 `StartCalendarInterval` 含 Weekday=6 Hour=18 Minute=30，且周一至周五仍为 21:30。

## 关联

- `.cursor/rules/daily-report.mdc`
- `feedback_daily_report_dual_mac_before_2130.md`
- `playbook_daily_weekly_report.md`
