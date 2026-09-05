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

## 验证（2026-09-05 更正）

**不够：** 只 assert `build_detailed_reply is None` / 函数签名有 `workbook_date`。09-03 补丁因此绿灯，但 09:01 仍用写死 1/2 条秒回。

**必须：** 正文无「禁止秒回模板」；`fallback` stub 解析不出编号【又初】项；**09:01 不在兜底窗口**；未进站正文写明「原文未进站」。

`omdb/tgbot/` 不入 CHcode → 走 memory 补丁。旧机：

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_workbook_no_instant_ack.sh
```

**禁止**在 new-mac 上长期跑 bot（旧机权威）；本机只改源码/打补丁。

## 关联

- `feedback_workbook_progress_list_plus_owned_cutoff.md`
- `patches/tgbot-workbook-no-instant-ack/`
- `scripts/apply_tgbot_workbook_no_instant_ack.sh`
