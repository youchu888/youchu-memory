# ETL / Dev Session 统一放 ops_system 分层目录

**适用**：CHcode 所有新建或迁移的表级 ETL、DDL、dev session 工件（spec/design/playbook/task.yaml/memory）。

## 硬规则

1. **禁止**在仓库根目录创建 `dwd_*` / `dws_*` / `dwm_*` / `ads_*` / `dim_*` 等表级 session 文件夹。
2. **所有** SQL（ETL + DDL）与 session 文档必须落在 `ops_system/` 下**对应数据层**子目录：
   - DWD → `ops_system/02.dwd/`
   - DWM → `ops_system/03.dwm/`（若有）
   - DWS → `ops_system/04.dws/`
   - ADS → `ops_system/05.ads/`
   - DIM → `ops_system/06.dim/`
   - DW  → `ops_system/01.dw/`
3. **每表一目录**，目录名与海豚 task / 库表一致，例如：
   - `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/`
   - `ops_system/02.dwd/job_dwd_user_type_d/dwd_user_register_d_v2/`
4. **双扫 / 口径变更**：在**既有** SQL 文件上修改，**不要**新建平行 `_d_d` 目录替代原路径。
5. **Git 入库**：`ops_system` 下仅 `*.sql` 提交；`*.md` 与 `task.yaml` 本地留存（见 `.gitignore`），但物理位置仍在 ops_system 表目录内。

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
| `/CHcode/dws_register_attribution_metrics_d_d/` | `ops_system/04.dws/dws.dws_register_attribution_metrics_d_d/` |
| 新建 `dwd_user_login_d_d/` 平行目录做双扫 | 改 `ops_system/02.dwd/.../dwd_user_login_d_v2/*.sql` |
| session 文档散落根目录或 `.cursor/` 当 canonical | 文档跟 SQL 同目录，在 ops_system |

## 验证

```bash
# 根目录不应有表级 session
ls -d /CHcode/dwd_* /CHcode/dws_* 2>/dev/null && echo BAD || echo OK

# SQL 应在 ops_system
git ls-files 'ops_system/**/*.sql' | rg 'register_attribution_metrics'
```

## 关联

- lesson：`lessons/2026-06-24-ops-system-etl-directory-layout.md`
- 目录地图：`project_chcode_directory_index.md` §1
