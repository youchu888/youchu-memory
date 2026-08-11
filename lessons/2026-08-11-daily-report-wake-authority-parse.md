---
date: 2026-08-11
tags: [daily-report, launchd, tg, AUTHORITY_HOST]
severity: high
domain: ops
---

# 日报 wake 读 AUTHORITY_HOST 禁止整文件去空白

## 背景

2026-08-11 21:30 `com.youchu.daily-report-wake` 已触发，但未写入 `AGENT_LOOP_WAKE_DAILY_REPORT`，主人未见 TG 私聊日报。

## 坑 / 错误做法

`daily-report-wake.sh` 用 `tr -d '[:space:]'` 读 `work-log/AUTHORITY_HOST`。文件含注释行时，换行被删后注释与 `old-mac` 粘成一串，权威机校验失败并 `skip`。

日志形如：`skip: host=old-mac not authority=#正式日报权威主机...old-mac`

## 正确做法

1. 与 Python 一致：跳过空行 / `#` 注释，取首个非注释行
2. 改 `.cursor/scripts/daily-report-wake.sh` 后同步到  
   `~/Library/Application Support/youchu-agent-bus/scripts/daily-report-wake.sh`
3. 定稿后仍须 `post_daily_report_to_dm.py`（仅 old-mac）

## 验证

```bash
bash ~/Library/Application\ Support/youchu-agent-bus/scripts/daily-report-wake.sh
# 未推送日应出现 woke AGENT_LOOP_WAKE_DAILY_REPORT
# 已推送日 skip: already posted DM
tail -5 "$HOME/Library/Application Support/youchu-agent-bus/state/daily-report-wake.log"
```

## 关联

- lesson：`2026-08-10-daily-report-21-30-wake-launchd.md`
- 脚本：`.cursor/scripts/daily-report-wake.sh`
- 配置：`~/.dc-platform/memory/work-log/AUTHORITY_HOST`
