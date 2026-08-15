# Feedback：日报定稿后推送 TG 私聊（仅 old-mac）

**来源**：主人 2026-08-04

## 正确做法

1. 双机汇总后由 **old-mac** 定稿
2. 跑：`python3 ~/.dc-platform/memory/scripts/post_daily_report_to_dm.py`
3. new-mac 默认跳过（非权威）；勿在新机自动推
4. **自动链路**：wake（周一至周五 21:30 / 周六 18:30）必须被 cursor-executor 解析 `AGENT_LOOP_WAKE_DAILY_REPORT`（不能只认 AGENT_BUS）；fallback（+15 分钟）稿在则直推、稿不在则直跑写稿。写 lesson 不算修完。

## 关联

- canonical 脚本：`memory/scripts/post_daily_report_to_dm.py`
- playbook / daily-report.mdc
