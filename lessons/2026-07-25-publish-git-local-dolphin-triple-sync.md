# 发布前三处代码必须一致（git / 本地 / 海豚）

**日期**：2026-07-25  
**tags**：dolphin, git, publish, dev-session, datacheck  
**触发**：主人私聊#245；当日五档合表 test v137/v138 已发、git 仍 4 表 → 野花 bus#5481 FAIL

## 现象

- test 海豚 live SQL 含 `stat_grain` + UNION ALL daily
- `origin/dev` 仍是旧 4 表、无 `stat_grain`
- 审单人按 git 复核 → **不一致，不能过 pending**

## 规则

发布完成 = **git commit（已 push）+ 本地 ops_system + 海豚 live SQL** 三处同一版本。

## 固定流程

1. 改 SQL/DDL → commit → **push 先于或同步于海豚发布**
2. 平台 session artifact 对齐同一 commit
3. `publish-task-sql` 后拉海豚 SQL 与 `git show SHA:path` **diff 为空**
4. 对外汇报带 **commit SHA**（bus / 群 / 审单）

## 反例

只发海豚不 push git；或 push 了但没重发海豚 → 验数/审单必踩坑。
