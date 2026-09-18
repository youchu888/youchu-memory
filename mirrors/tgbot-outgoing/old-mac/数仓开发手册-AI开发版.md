# 数据中心数仓开发手册（AI Agent 版）

> 版本：2026-07-30 · 受众：又初 / Cursor / Codex / 协作 Bot  
> 权威剧本：`vscode-extension/server-mcp/prompts/a2a3/playbook/`

---

## 0. 冷启动（每次会话先做）

```
1. Read .cursor/.agent-memory-bootstrap.md
2. 按任务类型匹配 lessons/_index.md tags → 读完整 lesson
3. 查表/写字段前：aliases.md → sqlite3 metadata.db 确认列名
4. 新 ETL / 新表：必须建 dev-session（project_id=dmp/dc-parent）
```

**TASK-BRIEF 内化**（口语任务先落成）：
- TYPE: db | datacheck | dbprogramming | dolphin_test | dolphin_prod | complement | explain
- ENV: 轻量查数→test；对账/datacheck→prod 只读；写库/发海豚→test 先发
- DT: 默认 T-1，用户未说禁止扩窗

---

## 1.  playbook 路由（听到什么读什么）

| 用户/派单意图 | 读 |
|---------------|-----|
| 新建/改 task、升级 task_version、stage1-6 | `dev_platform_dev.md` |
| 审核、request-publish、prod publish、stage7 | `dev_platform_publish.md` |
| 动海豚 wf/task/schedule/补数 | `dolphin.md` |
| 写 SQL/ETL | `sql.md` + `etl.md` |
| 查数/对账 | `data_query.md` + playbooks |
| 写 spec | `spec_writing.md` |

开发剧本止于 stage6 commit；发布剧本从 stage7 接力。**禁止混读跳步。**

---

## 2. 硬规则（违反 = 复审必打回）

### 2.1 流程

- 新需求：**建 dev-session** → stage 1→7，禁止只本地 `ops_system/` 手搓当交付
- 禁止空标 stage done；`state_json` 须有 `stage4_db_check` / `stage5_prod_dryrun` / `stage6_commit` 等真产物
- 正式海豚改动：**publish-task-sql** / **publish-from-repo**；禁止手搓 REST 整包 PUT task_params
- **又初禁止自发 prod**；test 验完 → request-publish → 等知秋/admin
- git 交付：stage6 前必须 **push origin/dev**，验收以远程 SHA 为准

### 2.2 SQL / DDL

- 所有 `INSERT INTO/OVERWRITE ... SELECT` **必须显式 col_list**
- DDL 加列 + 写表 ETL **同批**发布；半上线 prod 定时秒挂
- SR 禁止 Hive 式 `PARTITION (dt='...')`；PK 表用 INSERT INTO upsert
- 改表前 rg 所有写该表的 task

### 2.3 验数

- datacheck 默认 **T-1**，未指定禁止扫 7/14/30 天
- 对账/datacheck 连 **prod** `my.cnf.prod`（52.221.240.167）；test 稀疏会产生假异常
- 三件套：PI SUCCESS + 分区有行 + 行数/指标合理
- hourly：≥2 slot，含跨日；PK upsert：≥2 dt 幂等重跑

### 2.4 海豚

- 改 task 五步法：check_no_running → OFFLINE → PUT → ONLINE wf → **schedule ONLINE**
- test/prod code 不通用；用 `wf_cross_env_map.yaml` + `find-task-by-name`
- DEPENDENT 跨 wf：先 `prod-sync/precheck`，missing 则拒同步
- ONLINE schedule 不能直接 PUT cron → OFFLINE → 改 → ONLINE

### 2.5 协作

- agent-bus 派单：60s ACK → 干活 → **reply 结案**（`agent_bus_send.py --reply-to-bus-id`）
- 狂人标「结论请回 bus」→ 验完直接 bus reply，禁止问主人「要不要发 bus」
- TG 群仅 `@youchu_ai_bot` / `@初儿` 等显式 @ 时回复；口语「又初」不回、也不解释为什么不回

---

## 3. 标准执行链（新 task · stage 1→6）

```
Step 0  业务真因：定位 task、prod 抽样验证方案、代价分析
Step 1  /start-modify（改已有）或建 session（新建）
Step 2  写 spec/design/SQL/task.yaml；session__lint 0 error
Step 3  publish-task-sql → test（每个 task_code 各发一次）
        complement_data → poll SUCCESS → test SR 查数（不看 log 里未渲染的 ${dt}）
        advance stage/4 done + 写入 stage4_db_check 证据
Step 4  prod 只读 dry-run（live SQL、最新分区、SELECT 小样本预测）
        advance stage/5 + stage5_prod_dryrun
Step 5  git commit + push origin/dev；advance stage/6 + stage6_commit.sha
── 开发剧本结束，交 publish 剧本 ──
```

### stage4 证据模板（写入 state_json）

```json
{
  "stage4_db_check": {
    "created": true,
    "etlRan": true,
    "playbookConfirmed": true,
    "etlMeta": {
      "pi_id": "...",
      "task_instance_id": "...",
      "dt": "YYYY-MM-DD",
      "row_count": 12345
    }
  }
}
```

---

## 4. 发布链（stage 7 · 通常 admin 执行，AI 指引+验五项）

前置：`stage_status.6=done`, `stage_status.7=pending`, git 已 push

```
Step A  审核：session 状态、owned_tasks prod 位置、git diff、test 证据
Step B  publish-from-repo（env=prod，每 task 单独推，带 session_code）
Step C  五项验证（每个 task 推完立刻跑）：
        a) PublishRun task_version 对齐 ok=true
        b) prod live SQL grep 关键字
        c) wf release_state ONLINE
        d) schedule releaseState ONLINE
        e) session stage_status.7=done
Step D  次日 cron 后查 MAX(etl_time)、COUNT、关键 NULL 率
```

**禁止**手工 `POST .../stage/7/status` 标 done（endpoint 会 400）。

---

## 5. MCP / API 速查

| 动作 | 工具/接口 |
|------|-----------|
| 列 session | `session_list` / `GET /api/v1/dev-sessions/index?project_id=dmp/dc-parent` |
| 写 artifact | `session_write_artifact` |
| 推进 stage | `session_advance_to_stage` |
| test 发 SQL | `dolphin__publish_task_sql` + `session_code` |
| test 补数 | `dolphin__complement_data` |
| prod 发版 | `publish-from-repo`（admin token，非 admin 403 正常） |
| 平台文档 | `GET /api/v1/platform/docs` + `/raw/{slug}` |
| agent-bus 发消息 | `.claude/database/scripts/notify/agent_bus_send.py` |

配置：`.claude/database/dc-platform.json`

---

## 6. 目录与文件约定

```
ops_system/
  02.dwd/   03.dwm/   04.dws/   06.dim/   _templates/
  <job_dir>/
    spec.md design.md playbook.md memory.md
    task.yaml  *.sql  *_ddl.sql
.claude/database/
  playbooks/<db>.<table>.md   # canonical 验数剧本
  reports/<table>/            # 当次核查报告
  my.cnf.test | my.cnf.prod
omdb/data/metadata.db         # 列名元数据（sqlite3 查）
```

- session 内 `.md` 可走平台持久化；**SQL/yaml 必须进 git**
- Spark 链路：`ops_system/_templates/spark_yarn_launcher.sh`，wrapper 先 step0 DDL bootstrap

---

## 7. 意图 → 动作映射（口语）

| 用户说 | AI 做 |
|--------|-------|
| 查一下、探表 | test my.cnf，T-1 |
| 验数、对账、核查 | prod my.cnf，读 playbook，报告写 reports/ |
| 改 SQL、加字段 | 建/开 session → test 先发 → 禁止 prod |
| 补数 | complement，hourly 注意跨日宏 |
| 解释口径 | explain，读 knowledge/design，不跑库也可 |
| 上线 prod | 只准备 request-publish 材料，等知秋令 |

---

## 8. 输出纪律

- 群聊：先结论、短句、≤4 条 `·`，无 `##` 大标题
- 多步任务收尾：写 lesson + 更新 `_index.md`（又被纠正必须同会话改行为）
- 大结果写文件路径，对话只报 3 条结论
- commit message 含汉字说明（why）

---

## 9. 反面教材（lesson 浓缩）

1. INSERT 无 col_list → 加列静默错位（dim_user_all 2026-07-02）
2. 只 ALTER 不发 ETL → prod analyze 0 秒 FAIL
3. test 当 prod 结论 → 量级差 5~6 个数量级假异常
4. PI SUCCESS + 新列 0% → `enable_insert_strict=false` 静默 NULL
5. wf ONLINE 但 schedule OFFLINE → 定时不跑
6. 空标 stage done → stage7 审核界面打不开
7. project_id=dc-platform → 插件需求列表不可见

---

## 10. 自检命令

```bash
# agent-bus 未结案
.cursor/scripts/agent-bus-open.sh

# session 是否在列表
curl -H "Authorization: Bearer $TOKEN" \
  "http://54.255.236.159:8012/api/v1/dev-sessions/index?scope=mine&project_id=dmp/dc-parent"

# 列名
sqlite3 omdb/data/metadata.db "SELECT name, data_type, comment FROM columndefinition c
  JOIN tabledefinition t ON c.table_id=t.id WHERE t.database='dwd' AND t.name='...'"

# git 对齐
git fetch origin && git show origin/dev:<path>
```

---

## 关联规则文件（Cursor alwaysApply）

- `.cursor/rules/dev-platform-session-required.mdc`
- `.cursor/rules/dev-session-stage-artifacts-required.mdc`
- `.cursor/rules/datacheck-playbook.mdc`
- `.cursor/rules/agent-bus-session.mdc`
- `.cursor/rules/git-commit-chinese.mdc`
