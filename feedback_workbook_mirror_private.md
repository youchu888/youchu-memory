# Feedback：工作簿镜像到私聊

**来源**：主人 2026-08-31「工作簿也要镜像到私聊」

## 正确做法

每日群「今日工作簿」与发群进展，**都要进主人私聊**（与 agent-bus `status_mirror` 同一管道）：

- 原文入站：标题「今日工作簿」，不要求 `@又初`
- 发群进展：再推一份「又初→群」
- 同一天原文只推一次（`inbound_dm`）

## 错误做法

- 只发机器人群 / 只 mirror bus，私聊没有
- 因正文是 `【又初】` + `@worker_ant_bot` 就当旁听丢掉

## 关联

- `omdb/tgbot/group_target_filter.py` · `group_workbook_progress_handler.py`
- lesson `2026-08-31-工作簿也要镜像到私聊.md`
