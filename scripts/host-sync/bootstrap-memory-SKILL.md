---
name: bootstrap-memory
description: >-
  新 Agent 或 Cursor 重启后的冷启动：按索引加载历史记忆、习惯、纠错与 lesson。
  在 sessionStart 已生成 .cursor/.agent-memory-bootstrap.md 后，又初按本 skill 深入检索。
---

# 记忆冷启动（bootstrap-memory）

## 触发

- 新 Agent 对话
- Cursor 重启后首次对话
- 用户说「加载记忆」「读历史经验」

## 第一步（自动）

`sessionStart` hook 已生成：

```
.cursor/.agent-memory-bootstrap.md   ← 本工作区启动记忆包（必读）
~/.dc-platform/.session-bootstrap.json ← 路径指针
```

**轻量铁律**（详见 `~/.dc-platform/memory/MEMORY_LIGHT.md`）：

1. **只 Read bootstrap 一份**。规则不在启动包里，做到这件事再查
2. 按手头的事跑 `bash ~/.dc-platform/scripts/lookup-rules.sh 关键词`，对上的再读原文，最多 1～2 篇
3. 非 bus 任务 **跳过** bootstrap §0.5 历史未结案表
4. **禁止**整篇 Read `MEMORY.md` 或 `_index.md`

启动包硬注入（狂人 v2 对齐，**存量索引不整包灌入**）：

| 段 | 来源 | 作用 |
|----|------|------|
| A 规则 | `lookup-rules.sh` | 启动不读；做到再按关键词查红线和经验 |
| B OPEN | `MEMORY_OPEN.md` | 未结交接（≤3KB，结了删行） |
| C recent | lessons/feedback/project **mtime top-5** | 按时间最近动过（防只看 hot） |
| D high | severity:high **标题摘要** | 最多 12 条，不灌全文 |
| E/F | `_index` 速览 + session | 深读入口 |

**又初的第一动作**：`Read` 上述 bootstrap 文件，**再回复用户**。

## 第二步（按任务深入）

根据用户任务从 bootstrap 标题/tags 匹配，深入读取（全量在 `MEMORY.md` / `_index`，不在启动包）：

| 任务类型 | 检索 tags | 读取 |
|----------|-----------|------|
| 海豚发布/补数 | dolphin, complement, schedule | `lessons/*dolphin*` + feedback_dolphin* |
| 数据核查/对账 | datacheck, playbook | lessons + `feedback_report_before_saving_playbook` |
| SQL/ETL | sql, starrocks, dwd | feedback_starrocks*, feedback_no_dollar_bracket* |
| 归因 | attribution, per-app | lessons 20260603*, feedback_per_app* |
| 元数据 | metadata, openmetadata | project_metadata*, feedback_metadata* |
| 记忆维护 | memory, hygiene | `playbook_memory_hygiene.md` |

```bash
rg -l "dolphin|complement" ~/.dc-platform/memory/lessons/
```

有 MCP 时：`memory.list` → `memory.read(rel_path)` 读完整条目。

## 第三步（活跃 session）

若用户在某个 Dev Session 目录工作，额外读：

- `<session>/memory.md`（只追加的会话决策）
- `<session>/spec.md` / `design.md` / `task.yaml`

路径见 bootstrap §F 或 `.cursor/projects/registry.yaml`。

## 禁止

- **禁止**在未读 bootstrap 前直接写 SQL / 跑海豚 / 落盘 playbook
- **禁止**重复问用户已在 feedback / lesson / PINNED 里写明的偏好
- **禁止**只看 high/hot 而忽略 §C「按时间最近动过」
- bootstrap 是摘要；细节以 `memory.read` 原文为准
- 全量 `MEMORY.md` 是索引，不是每次必读正文

## 验证

```bash
bash ~/.dc-platform/scripts/load-memory-context.sh /Users/mac/Desktop/CHcode
wc -c .cursor/.agent-memory-bootstrap.md ~/.dc-platform/memory/MEMORY_OPEN.md
head -40 .cursor/.agent-memory-bootstrap.md
```
