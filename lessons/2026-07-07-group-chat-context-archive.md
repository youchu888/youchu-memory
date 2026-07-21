---
date: 2026-07-07
tags: tg, group, context, memory, archive, tgbot
severity: normal
---

# 监控群聊上下文定时归档

## 背景

监控群（`MONITOR_GROUP_CHAT_ID`）旁听 + 私聊 + agent-bus 信号统一写入 `.cursor/tgbot-bridge/context.jsonl`。长期不清理会膨胀，prompt 侧也只读最近 12 条，历史上下文无法检索。

## 架构

| 层 | 路径 | 说明 |
|----|------|------|
| 热上下文 | `.cursor/tgbot-bridge/context.jsonl` | 最近 150 行 / 24h 内 |
| 冷归档 | `~/.dc-platform/memory/group_chat/archive/YYYY-MM-DD.md` | 按日 Markdown 摘要 |
| 机器索引 | `~/.dc-platform/memory/group_chat/_search.jsonl` | 关键词检索 |
| 人读索引 | `~/.dc-platform/memory/group_chat/_index.md` | 日期表 + 链接 |

## 正确做法

1. **自动**：`bot_health._maybe_cleanup_artifacts()` 每小时触发 `group_context_archiver.maybe_run_scheduled()`，默认 6h 间隔节流。
2. **手动**（需 tgreport 环境）：
   ```bash
   cd omdb/tgbot && source _env.sh
   python scripts/run_group_context_archive.py --force
   ```
3. **环境变量**（`omdb/tgbot/.env`）：
   - `GROUP_CONTEXT_ARCHIVE_ENABLED=true`
   - `GROUP_CONTEXT_KEEP_LINES=150`
   - `GROUP_CONTEXT_HOT_HOURS=24`
   - `GROUP_CONTEXT_ARCHIVE_INTERVAL_SEC=21600`
4. **检索**：`prompt_builder` 在 `work_memory.search` 之后追加 `group_context_archiver.search_archived`；Cursor 启动包 §0.6 注入 `_index.md` 摘要。

## 验证

- `context.jsonl` 行数 ≤ `GROUP_CONTEXT_KEEP_LINES`
- `~/.dc-platform/memory/group_chat/_index.md` 有对应日期行
- 归档脚本 `--force` 返回 `ok: true`

## 变更记录

- 2026-07-07：初版；首次归档 555 条 → 7 天 Markdown
