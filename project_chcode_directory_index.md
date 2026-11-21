---
name: CHcode directory index
description: dc-parent 仓库目录地图——查 ETL/SQL/服务/工具时先读本索引定位路径。
type: project
---

# CHcode（dc-parent）目录索引

> **维护人**：又初 · **更新**：2026-11-21（bus#14190 按仓库重组对照表改路径）
> **工作区**：`/Users/mac/Desktop/CHcode` · **归属**：dc-platform
> **检索**：按任务类型跳转到对应区块，再 `rg` / `Glob` 细找文件。

---

## 0. 又初/agent 配置（优先读）

| 路径 | 用途 | 何时读 |
|------|------|--------|
| `.cursor/.agent-memory-bootstrap.md` | 启动记忆包（自动生成） | 每次新 Agent / 重启 |
| `.cursor/rules/you-chu-agent.mdc` | 又初身份 + 冷启动协议 | 自动 |
| `.cursor/projects/registry.yaml` | 活跃 Dev Session 列表 | 接手任务 |
| `.cursor/skills/` | bootstrap-memory / self-evolve | 记忆加载、任务收尾 |
| `~/.dc-platform/memory/MEMORY.md` | 公共记忆总索引 | 跨 session 检索 |
| `~/.dc-platform/projects/INDEX.md` | 全局项目注册 | 查 session 状态 |

---

## 1. 数据开发（ETL / SQL）— 日常主战场

> **仓库重组（2026-11-21）**：顶层拆成 `data-jobs/`（作业）+ `data-platform/`（平台）。逐文件对照：`data-platform/docs/repo_reorg_20261121_path_mapping.tsv`（列 old/kind/new/note）。旧名 `ops_system/`→`data-jobs/dolphin/`；`spark/`→`data-jobs/spark/`。

| 路径 | 层/内容 | 说明 |
|------|---------|------|
| **`data-jobs/dolphin/`** | dw/dwd/dwm/dws/ads/dim | **主 ETL 源码树**（原 `ops_system/`）；海豚 task 与目录一一对应 |
| `data-jobs/dolphin/02.dwd/` | DWD 明细 | 按事件类型分子目录 `job_dwd_*` |
| `data-jobs/dolphin/04.dws/` | DWS 汇总 | 每表一目录，含 `{table}.md` + SQL |
| `data-jobs/dolphin/06.dim/` | DIM 维度 | |
| `data-jobs/dolphin/05.ads/` | ADS 应用层 | |
| `data-jobs/dolphin/01.dw/` | DW 宽表 | `dw_user_event_detail` 等 |
| **`data-jobs/spark/`** | Spark 日批/影子 | 原根目录 `spark/` |
| `data-jobs/checks/` | 对账/核查 SQL | 含原 `ops_system/00.pipeline/recon/` 等 |
| `data-jobs/dolphin/_legacy_db/` | 旧 `db/` mirror | 历史 SQL；日常以 dolphin 层为准 |
| `data-jobs/archive/spark_legacy/spark_migrate/` | 新分/迁移稿 | 原 `ops_system/spark_migrate/` |
| `dolphin_ops/scripts/` | 海豚发布/补数 | `deploy_*` `complement_*` |
| `dolphin_ops/config/` | 海豚环境配置 | |

### Dev Session（七步流工件）— **一律在 data-jobs/dolphin 表目录内**

> **禁**仓库根 `dwd_*` / `dws_*` 等表级文件夹。SQL + 文档同目录，按数据层落位：
> DWD→`02.dwd/` · DWS→`04.dws/` · ADS→`05.ads/` · DIM→`06.dim/`
> 详见 `feedback_ops_system_etl_directory_layout.md`（布局约定仍有效，根目录已改名）

| 路径 | 状态 | 表/主题 |
|------|------|---------|
| `data-jobs/dolphin/04.dws/dws.dws_register_attribution_metrics_d_d/` | 进行中 | 归因看板日指标 |
| `data-jobs/dolphin/04.dws/dws.dws_register_attribution_result_d/` | 已上线 | 注册归因结果 |
| `.cursor/dev-sessions/dw明细表迁移/` | phase2 | dw 明细 4 路 + DWS 渠道 3 表 |
| `.cursor/dev-sessions/dws_user_first_recharge_retention_d_h/` | 进行中 | 首充留存 |
| `pending/` | 模板 | 新任务脚手架（复制到 dolphin 对应层后开发） |

每表目录标准工件：`{table}.sql` `{table}_ddl.sql`（git）+ `spec.md` `design.md` `playbook.md` `task.yaml` `memory.md` `README.md`（本地）

---

## 2. 数据库知识与核查

| 路径 | 用途 |
|------|------|
| `.claude/database/aliases.md` | 业务名 → 表名映射 |
| `.claude/database/metadata/project_metadata.md` | 表元数据、业务域、状态 |
| `.claude/database/metadata/program_mappings.md` | 表 → ETL 程序路径 |
| `.claude/database/metadata/event_tracking_metadata.md` | 埋点事件属性 |
| `.claude/database/playbooks/` | **核查剧本**（datacheck 最重要资产） |
| `.claude/database/reports/` | 当次核查报告 |
| `.claude/database/knowledge.md` | 项目数据库知识 |
| `.claude/database/scripts/` | 批量修复脚本 |
| `.claude/commands/` | `/db` `/datacheck` `/dbprogramming` 命令 |
| `.claude/dolphinscheduler.json` | 海豚 API token |

---

## 3. DC Platform 平台（AI 禁改源码）

| 路径 | 用途 | AI 权限 |
|------|------|---------|
| `data-platform/vscode-extension/` | VS Code/Cursor 插件 + server-mcp（原 `vscode-extension/`） | ❌ 禁改 |
| `data-platform/dc-platform-server/` | 后端 API（原 `dc-platform-server/`） | ❌ 禁改 |
| `data-platform/pipeline-runner/` | 调度 runner（原根 `pipeline-runner/`） | ❌ 禁改核心 |
| `CODE_INDEX.md` | 仓库代码地图（根） | 只读参考 |
| `data-platform/docs/repo_reorg_20261121_path_mapping.tsv` | 重组新旧路径对照 | 改记忆路径时必对 |
| `data-platform/vscode-extension/dc-platform-*.vsix` | 插件安装包 | 只读 |

平台运行时状态在插件 globalStorage，**不在工作区**。

---

## 4. Java 服务（Maven 多模块 `pom.xml`）

| 模块 | 职责 |
|------|------|
| `event-tracking-service/` | 埋点上报 + 渠道对外 API → Kafka |
| `ops-api-service/` | 运营系统 BFF 查询 API |
| `event-etl/` | 事件 ETL |
| `event-check/` | 事件质量检查 + Flink 文档 |
| `dc-analyse-udf/` | StarRocks UDF |
| `dc-flink-realtime/` `dc-flink-udf/` `flink-job/` | Flink 实时 |
| `data-load-paimon-s3/` `starrocks-to-paimon-s3/` | Paimon/S3 数据加载 |
| `dc-mata-data-admin/` | 元数据管理（OpenMetadata 集成） |
| `dc-event-quality-inspection/` | 数据质检（pom 中已注释） |

`project.md` — 项目归属（TQ-002 DMP）、责任人、服务说明。

---

## 5. 独立子项目 / 归档

| 路径 | 说明 | 记忆规则 |
|------|------|----------|
| `data-jobs/archive/omdb/` | 原 `omdb/`（DB 工具 + TG Bot 归档） | 规则见归档内 CLAUDE；现网 tgbot 路径以本机部署为准 |
| `data-jobs/archive/operating-system/` | 原 `operating-system/` 旧版运营 SQL | 历史参考，非主 ETL 树 |
| `data-jobs/docs/` · `data-platform/docs/` | 文档（原根 `docs/` 已拆） | 平台文档优先 `data-platform/docs/` |

---

## 6. 可忽略 / 本地-only

| 路径 | 说明 | 建议 |
|------|------|------|
| `.idea/` | IntelliJ 配置 | 不用 IDEA 可删；已在 .gitignore |
| `.vscode/` | 工作区设置（含 dcPlatform.*） | **保留** |
| `*/target/` | Maven 编译产物 | 忽略 |
| `dolphin_ops/.venv/` | Python 虚拟环境 | 忽略 |
| `__pycache__/` | Python 缓存 | 忽略 |

### 已清理（2026-06-17）

- ~~`-d/`~~ — 误留 extension 编译垃圾
- ~~`.dc-platform/`~~ — 旧工作区目录（已迁 `~/.dc-platform/`）
- ~~`.github/java-upgrade/`~~ — Java 升级工具残留 hook

---

## 7. 检索捷径

| 我想… | 先去哪 |
|--------|--------|
| 找某张表的 ETL | `rg "表名" data-jobs/dolphin/ data-jobs/spark/` → `program_mappings.md` |
| 跑数据核查 | `.claude/database/playbooks/<db>.<table>.md` |
| 查业务别名 | `.claude/database/aliases.md` |
| 海豚发布 | `dolphin_ops/scripts/deploy_*` + lesson `dolphin*` |
| 新建表开发 | `pending/` 复制 → 登记 registry.yaml |
| 查平台 MCP 工具 | `data-platform/vscode-extension/server-mcp/src/tools/` |
| 查 Java 接口 | `project.md` → 对应 `*-service/` |
| 旧路径改新 | `data-platform/docs/repo_reorg_20261121_path_mapping.tsv` |

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-17 | 初建；清理 -d / .dc-platform / .github |
| 2026-11-21 | bus#14190：按 repo_reorg 对照表改路径（ops_system→data-jobs/dolphin 等） |
