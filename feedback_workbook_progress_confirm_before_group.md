# Feedback：工作簿进展 = 核对真实进度后自动发群

**来源**：主人 2026-07-29 澄清；**2026-08-07 再强调**（进展天天一样 / 新大活要登簿）

## 正确做法

1. **每天**按工作簿里又初负责的几项，**实际查** prod/test 分区 + 平台 session + 当日 work-log，整理后再发
2. **自动发机器人群**，不需要主人确认
3. **禁止**日复一日固定模板文案（如写死「Paimon SF-81 DONE」「08-06 已完成某某补丁」）
4. 「已做」必须带**当日探针数字**（最新分区 dt、行数）和/或 **当日 work-log 近况**；完成项也要拼近况，禁止只留历史套话
5. 探针失败要老实说「读不到分区」，不要套旧话术冒充进展
6. **新大活**（如大漏斗）判定要登簿 → 当天写 `workbook_supplemental.json` + `project_youchu_workbook_tasks.md`「自开任务」；**次日**群进展自动带上（见 `feedback_自开任务必须登工作簿.md`）

## 错误做法

- 发群前还要主人回「确认发群」（多余）
- 设备标签 / 停留 / 访问用硬编码旧进度，隔天正文几乎不变
- 探针空了仍发「phase-1 影子期在跑」一类套话
- 大活只建 session / 只写 materials，不登 supplemental，群进展永远看不到

## 关联

- `workbook_progress_service.py`（实时探针 + work-log 多目录）
- `omdb/tgbot/data/workbook_supplemental.json`
- `group_workbook_progress_handler.py`（默认直接发群）
- `feedback_自开任务必须登工作簿.md`
