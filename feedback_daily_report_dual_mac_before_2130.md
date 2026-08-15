# Feedback：日报必须先双机上传再同步再写（主人 2026-08-11）

## 正确顺序（不可颠倒）

1. **推送点前** · 新 Mac + 旧 Mac：当天任务写入 `.cursor/work-log/当日.md` 并推 **youchu-memory**
2. **互相同步**（`sync-memory-git` / `prepare_daily_report_sync`）拉齐 `hosts/new-mac` + `hosts/old-mac`
3. **再整理日报**（old-mac 定稿）
4. **推 TG**（`post_daily_report_to_dm.py`，仅 old-mac）

## 定时（主人 2026-08-15）

| 时间 | 谁 | launchd |
|------|----|---------|
| 周一至周五 21:20 / 周六 18:20 | 两台 | `com.youchu.pre-daily-report-flush` |
| 周一至周五 21:30 / 周六 18:30 | old-mac | `com.youchu.daily-report-wake` |
| 周一至周五 21:45 / 周六 18:45 | old-mac | `com.youchu.daily-report-fallback` |

周日不推。

## 安装

```bash
# 两台都跑
bash ~/.dc-platform/memory/scripts/install-pre-daily-report-flush-launchd.sh
# 仅旧机
bash /Users/mac/Desktop/CHcode/.cursor/scripts/install-daily-report-wake-launchd.sh
bash /Users/mac/Desktop/CHcode/.cursor/scripts/install-daily-report-fallback-launchd.sh
```
