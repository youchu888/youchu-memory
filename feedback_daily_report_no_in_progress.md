# Feedback：日报只写已完成；死锁少写；未完进明日；推送仅 old-mac

**来源**：主人 2026-08-04

## 正确做法

1. `【今日结果】`**只写已完成项**，末尾只标「已完成」
2. `【死锁阻碍】**尽量留空**（不要常规堆卡点）
3. 未完成项 → `【明日动作】`（可多条）
4. 禁止「进行中 / 待确认」
5. 先双机多 Agent 汇总再写
6. **自动生成 + TG 私聊推送由 old-mac 执行**；new-mac 只贡献 hosts，不自动推

## 关联

- `.cursor/rules/daily-report.mdc`
- `playbook_daily_weekly_report.md`
- `omdb/tgbot/scripts/post_daily_report_to_dm.py`（本机副本）
- **canonical（双机同步）**：`~/.dc-platform/memory/scripts/post_daily_report_to_dm.py`
