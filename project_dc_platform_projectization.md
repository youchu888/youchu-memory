---
name: dc-platform projectization
description: All dev sessions belong to dc-platform; public memory unified at ~/.dc-platform/memory/
type: project
---

# dc-platform 项目化与记忆统一

## 背景

2026-06-17 用户要求按项目化管理：所有 Dev Session 指向 dc-platform，公共记忆集中到单一目录，并建立自我进化 + 定期存档机制。Agent 定名 **又初**。

## 结构

| 资源 | 路径 |
|------|------|
| 公共记忆 | `~/.dc-platform/memory/MEMORY.md` |
| lesson | `~/.dc-platform/memory/lessons/` |
| 项目索引 | `~/.dc-platform/projects/INDEX.md` |
| 工作区注册 | `<ws>/.cursor/projects/registry.yaml` |
| 启动包 | `<ws>/.cursor/.agent-memory-bootstrap.md` | sessionStart 按索引自动生成，又初冷启动必读 |
| 存档脚本 | `~/.dc-platform/scripts/archive-memory.sh` |

## 约定

- `task.yaml` → `project: dc-platform`；海豚项目名写 `dolphin_project`
- 会话记忆仍在 `<session>/memory.md`（只追加）
- sessionEnd hook 触发存档（7 天节流）；`--force` 强制
- 又初规则：`.cursor/rules/you-chu-agent.mdc`

## 验证

- `ls ~/.dc-platform/memory/MEMORY.md`
- `cat ~/.dc-platform/.session-bootstrap.json`
- `bash ~/.dc-platform/scripts/archive-memory.sh --force` → `archives/YYYY-MM/YYYY-MM-DD/`
