---
date: 2026-06-24
tags: [ops_system, etl, sql, directory, dev-session, chcode]
severity: high
domain: ops
---

# ETL 工件禁止散落仓库根，统一 ops_system 分层目录

## 背景

开发 `dws_register_attribution_metrics_d_d` 时曾在仓库根建 `dws_register_attribution_metrics_d_d/` 并提交 git；双扫改造时也曾误在 `ops_system` 旁新建 `_d_d` 平行目录。用户要求：**SQL 与 session 一律进 ops_system 对应层目录，不要乱放。**

## 坑 / 错误做法

1. 在 `/CHcode/dws_xxx/`、`/CHcode/dwd_xxx/` 建 dev session（与 ops_system 重复、难找、易误提交）。
2. 双扫时在 `dwd_user_login_d_d/` 等新目录写 ETL，而不是改 `dwd_user_login_d_v2/` 原文件。
3. 只把 SQL 放 ops_system、文档留根目录——工件分裂两处。

## 正确做法

按**库表层级**选 `ops_system` 子树，**每表一目录**，SQL 与文档同目录：

```
ops_system/
├── 01.dw/
├── 02.dwd/job_dwd_*/{table}/
├── 04.dws/{db.table_dir}/
├── 05.ads/
└── 06.dim/job_dim_*/
```

示例（归因看板日指标）：

```
ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/
├── dws_register_attribution_metrics_d_d.sql      # git ✅
├── dws_register_attribution_metrics_d_d_ddl.sql  # git ✅
├── spec.md design.md playbook.md task.yaml memory.md README.md  # 本地，gitignore
```

- **修改既有逻辑**（双扫、口径）：编辑原路径 SQL，不新建平行目录。
- **Git**：仅 `*.sql` 入库；md/yaml 仍在 ops_system 表目录本地保存。

## 验证

- `git ls-files` 无仓库根 `dwd_*` / `dws_*` session。
- 目标表 SQL 路径在 `ops_system/{NN}.{layer}/` 下且与 `program_mappings.md` 一致。

## 关联

- feedback：`feedback_ops_system_etl_directory_layout.md`
- 目录索引：`project_chcode_directory_index.md` §1
- `.gitignore`：`ops_system/**/*.md`、`ops_system/**/task.yaml`；根目录 `dwd_*`/`dws_*` 拦截
