---
date: 2026-06-18
tags: [sql, lint, dolphin, dc-platform, etl]
severity: high
domain: sql
---

# ETL SQL 文件头三行声明（task / doc / params）

## 背景

归因任务 `dws_register_attribution_result_d.sql` 发布测试海豚时 DC Platform lint 报 `missing_header_task/doc/params`；此前补数虽 SUCCESS，但缺 `task.yaml` 导致 params 未声明。

## 坑 / 错误做法

- SQL 文件头只写业务说明注释，无 `-- task:` / `-- doc:` / `-- params:`
- 目录无 `task.yaml`，SQL 引用 `${pt}` `${dt}` 时 lint 报 undeclared param
- 注释里写 `pt/dt` 或 `${pt}` 字面量 → `forbidden_placeholder_in_comment` **error**（阻断发布）

## 正确做法

**每个海豚 ETL `.sql` 前 30 行内必须有：**

```sql
-- task: <海豚任务名，与 task.yaml task.name 一致>
-- doc: <一句话口径说明>
-- 频率: daily | hourly | ...
-- params: pt, dt          # 逗号分隔；无参写「无」
-- 幂等: ...
-- 上游: ...
-- ============================================================
```

**同目录必须有 `task.yaml`**，声明 SQL 主体里所有 `${name}`：

```yaml
params:
  - name: dt
    type: date
    required: true
    dolphin_macro: yyyy-MM-dd-1
  - name: pt
    type: string
    required: true
    dolphin_macro: yyyyMMdd-1
```

**硬规则（sql_lint.py）：**

| 位置 | 允许 | 禁止 |
|------|------|------|
| SQL 主体 | `${name}`、`$[yyyy-MM-dd-1]` | `@var` `:name` `?` |
| 注释 | 纯文字 | 任何 `${...}` `$[...]` 字面量 |

分区写法：`PARTITION (p${pt})` 在**主体**合法；注释里写「分区 p+pt」而非 `${pt}`。

## 验证

- VS Code / DC Platform：`missing_header_*` 消失；`referenced_params` 与 task.yaml 一致
- 发布前 `session.lint(code)` 或海豚 put 前 lint `ok=true`（无 error）

## 关联

- 规范：`dc-platform-server/app/services/sql_lint.py`
- 范例：`ops_system/04.dws/dws_user_tag_d_d/dws_user_tag_d_d.sql`
- 已修：`ops_system/04.dws/dws.dws_register_attribution_result_d/`、`ops_system/06.dim/job_dim_user_attribution_channel_apply/`
