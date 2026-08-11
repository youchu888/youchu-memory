# 记忆周清理 playbook（又初）

> 对齐狂人 bus#6361：沉前查重 + 周体检，否则「记了很多次还犯」= 数据质量问题。  
> **不删存量百科**；目标是去重、归档僵尸 project、压瘦 OPEN。

## 何时跑

- 每周一次（建议周五或周日）
- 同一主题一天被纠正 ≥2 次时，立刻加跑「矛盾合并」段

## 命令

```bash
bash ~/.dc-platform/scripts/memory_weekly_hygiene.sh
# 仅报告不备份：
bash ~/.dc-platform/scripts/memory_weekly_hygiene.sh --dry-run
```

## Checklist

1. [ ] 备份：脚本默认拷到 `archives/YYYY-MM/memory-hygiene-*/`
2. [ ] `MEMORY_OPEN.md` ≤3KB；已结项删行
3. [ ] `PINNED.md` ≤30 条；过时红线降级到 feedback
4. [ ] 扫重复簇：同主题 lesson + feedback 是否各说各话 → **更新老节点**，少建新 id
5. [ ] `project_*` 是否有退出条件；已结 → 归档或改 status
6. [ ] bootstrap 体积：`wc -c .cursor/.agent-memory-bootstrap.md`（目标远小于旧版 ~100KB）
7. [ ] 自检：清空上下文后，只靠 OPEN + pinned + 最近动过，能否续昨天未完？

## 召回并轨（lesson ↔ feedback）

- 「我错了→以后这么做」优先落 **feedback_** 或更新已有 feedback；lesson 记可复现运维步骤时，索引行注明 `see feedback_xxx`
- 冷启动：**不**再把全部 feedback 列表灌进 bootstrap；只灌 pinned + 最近动过 + 高优标题
- 深读仍按任务 tags：`rg` / MCP `memory.read` / `_index.md`
