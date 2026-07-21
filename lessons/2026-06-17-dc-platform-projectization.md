---
date: 2026-06-17
tags: [dc-platform, memory, project, archive]
severity: medium
domain: ops
---

# dc-platform 项目化：记忆统一与定期存档

## 背景

用户要求所有项目指向 dc-platform，公共记忆集中到 `~/.dc-platform/memory/`，并建立自我进化 + 定期存档。

## 坑 / 错误做法

- 在 `.claude/memory/` 与 `~/.dc-platform/memory/` 双写，索引分叉
- `task.yaml.project` 写海豚项目名「运营系统」，与 dev platform 项目混淆

## 正确做法

1. Canonical 记忆：`~/.dc-platform/memory/`（lessons 在子目录）
2. `task.yaml`：`project: dc-platform`，海豚名写 `dolphin_project`
3. 登记 session 到 `~/.dc-platform/projects/INDEX.md` + `.cursor/projects/registry.yaml`
4. 收尾写 lesson 并更新 `lessons/_index.md` + `MEMORY.md`
5. 存档：`~/.dc-platform/scripts/archive-memory.sh`（sessionEnd hook 自动触发）

## 验证

```bash
cat ~/.dc-platform/.session-bootstrap.json
ls ~/.dc-platform/memory/archives/*/
```

## 关联

- 规则：`.cursor/rules/you-chu-agent.mdc`
- skill：`.cursor/skills/self-evolve/SKILL.md`
- hook：`.cursor/hooks/session-start-memory.sh` / `archive-on-session-end.sh`
