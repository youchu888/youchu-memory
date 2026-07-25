# 协作习惯 · 发布前三处代码必须一致

**来源**：主人私聊#245（2026-07-25）

## 铁律

凡 **test / prod 海豚发布**，以下三处必须是**同一版本**（同一 commit、同一文件内容）：

| # | 位置 | 说明 |
|---|------|------|
| 1 | **Git** | `origin/dev`（或约定分支）已 push，commit SHA 可引用 |
| 2 | **本地** | `ops_system/` 工作区与将发布的 SQL/DDL 一致，无未 push 的漂移 |
| 3 | **海豚** | test/prod 线上 task SQL 与 git 对应路径 **字节级一致** |

## 禁止

- ❌ 只改本地 + 发海豚，**不 commit/push**（今日五档合表 v137/v138 超前 git → 野花 FAIL）
- ❌ 只 push git，**海豚仍是旧版**就报「已发布」
- ❌ 平台 session / pending 与 git 各写各的，审单人拉 git 对不上 live SQL

## 发布顺序（固定）

1. 本地改完 → **自检 diff**
2. **commit + push** `origin/dev`（记下 SHA）
3. 开发平台 session artifact / outputs 与 git **同 SHA 同步**
4. **再走** `publish-task-sql` / 海豚发布
5. **发布后复核**：`dolphin.get_task_sql` 或 API 拉 live SQL ↔ `git show SHA:path` diff 为空
6. 对外/bus/群：**带 commit SHA**，方便审单人对齐

## 验收口令

发布完成 = 能说出一句：

> git `abc1234` = 本地 `ops_system/.../xxx.sql` = 海豚 task vNNN 正文一致

不一致则**不算发布完成**，先对齐再验数、再 request-publish。
