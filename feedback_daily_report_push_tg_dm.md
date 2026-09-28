# Feedback：日报定稿后推送 TG 私聊（权威机 = AUTHORITY_HOST）

**来源**：2026-08-04；2026-09-28 权威迁 new-mac

## 正确做法

1. 汇总后由 **AUTHORITY_HOST**（当前 new-mac）定稿
2. 跑：`python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py`
3. 非权威机默认跳过；勿在非权威机自动推
4. **自动链路**（权威机 new-mac）：
   - 21:30 wake → IDE 可写精品稿
   - **21:45 fallback**：有稿直推；无稿则 `auto_draft_daily_report.py` 定稿并推（不依赖 Cursor）
   - **22:00 硬兜底**再确保一次（已推跳过）
   - 周六 18:45 / 19:00

## 关联

- canonical 脚本：`memory/scripts/post_daily_report_to_dm.py`、`auto_draft_daily_report.py`
- playbook / daily-report.mdc
- AUTHORITY_HOST：`memory/work-log/AUTHORITY_HOST`
- lesson：`2026-09-28-daily-report-fallback-auto-draft-post.md`
