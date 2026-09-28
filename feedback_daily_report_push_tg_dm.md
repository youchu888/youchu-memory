# Feedback：日报定稿后推送 TG 私聊（权威机 = AUTHORITY_HOST）

**来源**：2026-08-04；2026-09-28 权威迁 new-mac

## 正确做法

1. 汇总后由 **AUTHORITY_HOST**（当前 new-mac）定稿
2. 跑：`python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py`
3. 非权威机默认跳过；勿在非权威机自动推
4. **自动链路**：wake（周一至周五 21:30 / 周六 18:30）写入 `wake_feed` 的 `AGENT_LOOP_WAKE_DAILY_REPORT`，须被 IDE 主会话接住写稿；fallback（+15 分钟）稿在则直推、稿不在则再 wake

## 关联

- canonical 脚本：`memory/scripts/post_daily_report_to_dm.py`
- playbook / daily-report.mdc
- AUTHORITY_HOST：`memory/work-log/AUTHORITY_HOST`
