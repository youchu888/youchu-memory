# ETL / Dev Session 统一放 data-jobs/dolphin 分层目录

> **2026-11-21（bus#14190）**：原根目录 `ops_system/` 已迁为 `data-jobs/dolphin/`；分层编号与「每表一目录」规矩不变。对照表见 `data-platform/docs/repo_reorg_20261121_path_mapping.tsv`。

**适用**：CHcode 所有新建或迁移的表级 ETL、DDL、dev session 工件（spec/design/playbook/task.yaml/memory）。

## 硬规则

1. **禁止**在仓库根目录创建 `dwd_*` / `dws_*` / `dwm_*` / `ads_*` / `dim_*` 等表级 session 文件夹。
2. **所有** SQL（ETL + DDL）与 session 文档必须落在 `data-jobs/dolphin/` 下**对应数据层**子目录：
   - DWD → `data-jobs/dolphin/02.dwd/`
   - DWM → `data-jobs/dolphin/03.dwm/`（若有）
   - DWS → `data-jobs/dolphin/04.dws/`
   - ADS → `data-jobs/dolphin/05.ads/`
   - DIM → `data-jobs/dolphin/06.dim/`
   - DW  → `data-jobs/dolphin/01.dw/`
3. **每表一目录**，目录名与海豚 task / 库表一致，例如：
   - `data-jobs/dolphin/04.dws/dws.dws_register_attribution_metrics_d_d/`
   - `data-jobs/dolphin/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/`
4. **双扫 / 口径变更**：在**既有** SQL 文件上修改，**不要**新建平行 `_d_d` 目录替代原路径。
5. **Git 入库**：`data-jobs/dolphin` 下仅 `*.sql` 提交；`*.md` 与 `task.yaml` 本地留存（见 `.gitignore`），但物理位置仍在 data-jobs/dolphin 表目录内。

## 目录内标准工件

| 文件 | 入库 | 说明 |
|------|------|------|
| `{table}.sql` | ✅ | ETL |
| `{table}_ddl.sql` | ✅ | DDL |
| `spec.md` `design.md` `playbook.md` | ❌ | 需求 / 设计 / 核查 |
| `task.yaml` `memory.md` `README.md` | ❌ | 海豚绑定 / 会话备忘 / 业务口径 |

## 错误 vs 正确

| ❌ 错误 | ✅ 正确 |
|--------|--------|
| `/CHcode/dws_register_attribution_metrics_d_d/` | `data-jobs/dolphin/04.dws/dws.dws_register_attribution_metrics_d_d/` |
| 新建 `dwd_user_login_d_d/` 平行目录做双扫 | 改 `data-jobs/dolphin/02.dwd/.../dwd_user_login_d_v2/*.sql` |
| session 文档散落根目录或 `.cursor/` 当 canonical | 文档跟 SQL 同目录，在 data-jobs/dolphin |

## 验证

```bash
# 根目录不应有表级 session
ls -d /CHcode/dwd_* /CHcode/dws_* 2>/dev/null && echo BAD || echo OK

# SQL 应在 data-jobs/dolphin
git ls-files 'data-jobs/dolphin/**/*.sql' | rg 'register_attribution_metrics'
```

## 关联

- lesson：`lessons/2026-06-24-ops-system-etl-directory-layout.md`
- 目录地图：`project_chcode_directory_index.md` §1
