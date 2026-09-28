---
date: 2026-09-28
tags: [daily-report, launchd, tg, fallback, new-mac]
severity: high
domain: ops
---

# 日报按时推送：fallback 无稿自动定稿直推

## 背景

21:30 wake 只写 `wake_feed`；Cursor 未接住则无稿。21:45 旧兜底只会再 wake，仍不推送。

## 正确做法

1. 21:30 wake（权威机）→ IDE 有空可写精品稿
2. **21:45 fallback**：有稿直推；**无稿则 `auto_draft_daily_report.py` 从 work-log 定稿并推 TG**
3. **22:00 硬兜底**再跑同一脚本（已推则跳过）
4. 周六：18:45 / 19:00

```bash
bash .cursor/scripts/install-daily-report-fallback-launchd.sh
python3 ~/.dc-platform/memory/scripts/auto_draft_daily_report.py --date YYYY-MM-DD --dry-run
```

## 验证

```bash
plutil -p ~/Library/LaunchAgents/com.youchu.daily-report-fallback.plist | rg Hour
tail -30 "$HOME/Library/Application Support/youchu-agent-bus/state/daily-report-fallback.log"
```

## 关联

- `post_daily_report_to_dm.py` · AUTHORITY_HOST=new-mac
- feedback_daily_report_push_tg_dm.md
