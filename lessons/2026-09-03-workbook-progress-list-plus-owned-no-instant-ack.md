---
date: 2026-09-03
tags: [workbook, agent-bus, progress, cutoff, no-instant-ack]
severity: high
domain: ops
---

# 狂人 bus 清单问进度：清单主责 + 自开实责，统一查「截至汇报前」，禁止秒回

## 背景

主人 2026-09-03：不要秒回；狂人 bus 任务清单问进度时，要先确认清单里又初负责项 + 我们实际负责事项，统一查到汇报当前再报。天天一样 = 像没干活。

## 正确做法

1. 解析清单 → 又初负责项 → prod/task 板/work-log 实查
2. 并上自开实责（`workbook_supplemental.json` + task 板自开）
3. 口径 = 截至汇报前（D→cutoff D-1）；单条回复，禁精简秒回/双条 follow-up
4. 正文必须带当日探针数字（行数/分区），禁止复读硬编码

## 验证

```bash
cd omdb/tgbot && .venv/bin/python scripts/post_workbook_progress_to_group.py --dry-run
# 期望：先探针十余秒；含清单项 + supplemental；口径截至 T-1；无「精简·1~2分钟补发」
```

旧 Mac 跑 bot：同步本目录改动后 `bash omdb/tgbot/restart.sh`。

## 关联

- `feedback_workbook_progress_list_plus_owned_cutoff.md`
- `omdb/tgbot/workbook_progress_service.py`
- `omdb/tgbot/group_workbook_progress_handler.py`
