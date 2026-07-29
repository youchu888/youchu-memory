# Feedback：工作簿进展发群前必须主人确认

**来源**：主人私聊#248（2026-07-29）「每天确认以后再发群里。你现在每天都发的一样的」

## 铁律

1. **禁止** 09:01 `daily_fallback` / 工作簿点名自动往机器人群发进展
2. 默认流程：生成正文 → **只私聊主人草稿** → 主人回复「确认发群」才发群；「取消发群」作废
3. 正文必须是当日真实进展，禁止日复一日同一套模板腔

## 配置

- `GROUP_WORKBOOK_REQUIRE_OWNER_CONFIRM=true`（默认开）
- 私聊确认词：`确认发群` / `可以发` / `发群` / `确认`
- 取消：`取消发群` / `不要发` / `别发`

## 关联

- `omdb/tgbot/group_workbook_progress_handler.py`
- lesson：`lessons/2026-07-29-workbook-progress-confirm-before-group.md`
