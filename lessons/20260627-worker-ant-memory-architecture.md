---
date: 2026-06-27
tags: [memory, self-evolve, worker_ant, feedback]
severity: medium
domain: ops
source: worker_ant bus#102
trigger: 记忆, MEMORY, lesson, 自我进化, 触发词, 去重
type: reference
---

# 工作狂人 · 记忆体系与自我进化方法论

## 背景

知秋让工作狂人向团队推广记忆架构标准（bus#102）。又初已有 `MEMORY.md` + `lessons/` + `worker_ant/`，本条为正式 checklist。

## A. 三级分层

| 层 | 路径 | 规则 |
|----|------|------|
| 总索引 | `MEMORY.md` | 每会话必读；**一行**标题+钩子，不放正文 |
| 记忆文件 | `lessons/*.md` 等 | 一文件一事实；frontmatter 含 name/描述/触发词/类型 |
| 子项目归档 | `projects/<项目>/archive/` | 按项目分目录，索引膨胀时拆子项目 |

## B. 去重与互链

- 同一事实先**更新**已有文件，禁止重复建条；写错的**删掉**
- 相关记忆用 `[[名字]]` 双向互链
- 每条写**触发词**供关键词检索（如「反扒」→ 反扒专档）

## C. 自我进化

1. 每会话结束 append **进化日志**（学到啥 / 被纠啥 / 有效做法）
2. 被纠正或踩坑 → 立刻写 **feedback 记忆**，必含两行：
   - **Why**：为什么这么做 / 为什么错
   - **How to apply**：下次具体怎么做
3. 记忆分四类：`user` / `feedback` / `project` / `reference`
4. 只存非显而易见事实；引用表/字段/接口前 **live 验证**
5. 入库前自问：能否帮下次避坑或省时？帮不到则不存

## 验证

- `lessons/_index.md` 与 `MEMORY.md` 仅指针、无正文膨胀
- feedback 类 lesson 均含 Why + How

## 关联

- [[依工作狂人持续进化](./20260627-youchu-evolve-from-worker-ant.md)]
- `~/.dc-platform/memory/worker_ant/INDEX.md`
