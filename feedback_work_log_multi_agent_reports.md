# Feedback：work-log 跨 Agent 共享（日报/周报）

**适用**：又初及所有 Cursor Agent / 子 Agent · **仅本地** `~/.dc-platform/memory/work-log/`

## 问题

- 主会话与子 Agent transcript **分离**（`agent-transcripts/<id>/subagents/`）
- 父会话上下文**不自动**包含子 Agent 细节
- 整理日报/周报需人工翻多个 jsonl

## 约定

### 任务收尾（必做）

写入 **`CHcode/.cursor/work-log/YYYY-MM-DD.md`**（Asia/Shanghai，工作日）：

```markdown
- [TQ-002 | DMP] 一句话结果 — 已完成
```

子 Agent 完成委派任务后 **同样 append 当日文件**。

正式日报/周报 → **`.cursor/work-log/reports/`**。

### 开工前（日报/周报/同类任务）

1. 读 [`reference_work_calendar_cn.md`](../reference_work_calendar_cn.md) 确认是否工作日 / 自然周边界
2. 读 **`CHcode/.cursor/work-log/`** 当周 `YYYY-MM-DD.md` 与 `reports/*`
3. 可选：`grep` agent-transcripts、`git log --since=<周一>`
4. 读 `lessons/_index.md` 查坑

### 与 Git 关系

- work-log / 日报 / 周报在 **`.cursor/work-log/`**，仓库 `.gitignore` 已忽略 `.cursor/`
- lesson 仍在 `~/.dc-platform/memory/lessons/`

### transcript 路径（只读）

```
~/.cursor/projects/<project>/agent-transcripts/<session-id>/*.jsonl
~/.cursor/projects/<project>/agent-transcripts/<session-id>/subagents/*.jsonl
```

## 禁止

- 不要把 token/密码写进 work-log
- 不要用 work-log 替代 lesson（踩坑仍写 lessons/）
