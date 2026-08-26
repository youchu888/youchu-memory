---
date: 2026-08-26
tags: [tgbot, feedback, ux]
severity: high
domain: ops
---

# TG SQL 答完禁止再发「这个回答合适吗？」

## 背景

主人再次指出：查脏数据答完后仍弹出「这个回答合适吗？」+ 满意/不满意按钮。此前已改掉，后又被代码/patch 回滚启用。

## 坑 / 错误做法

- `_on_query_done` 末尾调用 `_ask_feedback_after_sql`
- 从 `patches/tgbot-parallel-agent/bot.py` 整文件覆盖回仓内 `omdb/tgbot/bot.py` 时把征询按钮带回来

## 正确做法

1. `_ask_feedback_after_sql` 保持空实现（直接 `return`）
2. `_on_query_done` **不要**调用征询
3. `cb_feedback` 可保留，仅兼容历史消息按钮
4. 改 bot 后须 **重启 tgbot** 才生效
5. 同步改 memory patch 副本，避免下次覆盖再启用

## 验证

答完 SQL 只看到业务结论（+ CSV），不再出现「这个回答合适吗？」。

## 关联

- feedback：`feedback_tg_no_ask_answer_ok.md`
- PINNED #21
- 代码：`omdb/tgbot/bot.py`
