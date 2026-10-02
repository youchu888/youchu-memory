# Feedback：工作簿进展 = 核对真实进度后自动发群

**来源**：主人 2026-07-29 澄清；**2026-08-07 再强调**（进展天天一样 / 新大活要登簿）

## 正确做法

1. **收到点名 → 先实查 → 再汇报**（主人 2026-10-02）：口径截至汇报前（D→D-1）；**严禁模板**
2. 按簿内主责 + 自开实责，**实际查** prod/test 分区/探针 + cutoff work-log + 平台 session，整理后 **只 bus 回狂人**（不回群）
3. **禁止**日复一日固定模板、禁止只抄任务板「进行中」
4. 「已做」必须带**探针数字**（dt、行数）和/或 **cutoff work-log 近况**；无实据就写「未查到实据」
5. 探针失败要老实说「读不到分区」，不要套旧话术冒充进展
6. **新大活**登 `workbook_supplemental.json` + 任务板「自开任务」；次日进展自动带上

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
