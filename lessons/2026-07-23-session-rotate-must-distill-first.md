---
date: 2026-07-23
tags: [tg, session-rotate, self-evolve, memory, feedback]
severity: high
domain: ops
---

# 会话轮换必须先沉淀再清空

## 背景

主人纠正：重启/清理 Cursor resume 上下文时，不能只图快把记忆抹掉；又初要持续学习进化。

## 坑 / 错误做法

- 只 `clear cursor_chat_id` / 关 session，直接新开
- 把「变快」当成「丢弃全部历史」

## 正确做法

1. **先蒸馏**：从 conversation_history + transcript 提炼要点 / lesson
2. 写入 `~/.dc-platform/memory/sessions/tg-rotate-*.md` + 热携带 `tgbot_session_carry.md`
3. 有实质铁律再落 `lessons/` 并更新 `_index.md` / `MEMORY.md`
4. **再轮换** resume；TG 通知里写明沉淀条数与归档路径
5. 新会话 system prompt 注入热携带

实现：`omdb/tgbot/session_memory_distill.py` + `agent_session_rotate.py`

## 验证

- 轮换后 `tgbot_session_carry.md` 非空
- 私聊通知含「已沉淀」
- 下一条私聊 prompt 含「上一会话沉淀」

## 关联

- `omdb/tgbot/agent_session_rotate.py`
- `omdb/tgbot/session_memory_distill.py`
- `omdb/tgbot/prompt_builder.py`
