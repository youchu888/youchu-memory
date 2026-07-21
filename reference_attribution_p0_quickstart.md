---
date: 2026-07-01
tags: [attribution, quickstart, gray, dolphin, datacheck]
maintainer: 又初
---

# 归因 P0 · 快速响应入口

> **何时读**：灰度对数 / test 补数 / 请示 prod 发布 / DAG 核对。  
> 完整方案 → [`reference_attribution_end_to_end_complete.md`](reference_attribution_end_to_end_complete.md)  
> rewrite_status 方案 → [`sessions/2026-06-30-attribution-rewrite-status-archive.md`](sessions/2026-06-30-attribution-rewrite-status-archive.md)  
> 今日归档 → [`sessions/2026-07-01-attribution-p0-daily-archive.md`](sessions/2026-07-01-attribution-p0-daily-archive.md)

## 1. 开工 30 秒

```bash
# 平台 doc 有无更新（Bearer 见 dc-platform.json）
curl -sS -H "Authorization: Bearer $(jq -r .token .claude/database/dc-platform.json)" \
  "http://54.255.236.159:8012/api/v1/platform/docs" | jq '.[] | select(.slug=="attribution_end_to_end_complete") | {updated_at}'

# 灰度开关
mysql --defaults-extra-file=.claude/database/my.cnf.test -e \
  "SELECT app_id,is_run,is_rewrite_channel FROM dim.dim_app_attribution_config WHERE is_rewrite_channel=1 OR app_id='SF-81';"
```

## 2. test 海豚（归因链 only）

| 项 | 值 |
|----|-----|
| project | 20524869250304 |
| wf | 21869820140416 (`wf_dws_汇总_日`) |
| result_d | 174729603403591 |
| channel_apply | 21962007716224 |
| metrics_d_d | 22127764280192 |

prod 同 canonical **`wf_dws_汇总_日`**，wf_code `20691538136576`（UI legacy `dws_日`）— `.claude/dolphin/wf_cross_env_map.yaml`

DAG 顺序：`等_dim` → result → apply → metrics → app_order…（快路 wf 已撤）

核对脚本：`python3 dc-platform-server/scripts/reorder_wf_attribution_first.py --dry-run`（或 MCP `dolphin_get_workflow` env=test）

## 2b. prod 海豚（权威名同 test：wf_dws_汇总_日）

| 项 | 值 |
|----|-----|
| project | 20524837077760 |
| wf（权威名） | **wf_dws_汇总_日** |
| wf_code | 20691538136576（海豚 UI legacy 仍显示 `dws_日`，勿当正式名） |
| result_d | 21043636973952 |
| channel_apply | 22179045765504 |

对照：`CHcode/.claude/dolphin/wf_cross_env_map.yaml` · prod DAG 拓扑与 test 不同，只 publish SQL 勿 remap 边

## 3. 灰度三条验收（playbook 全文见 playbooks）

业务日 `${dt}`，灰度 app `${app}`：

1. **总量守恒**：`dim_user_all` 该 app 用户数 apply 前后不变  
2. **organic 搬迁**：success 且可归因 organic → `channel = attributed_channel`  
3. **非灰度不变**：另选一 app channel 分布前后一致  

**坑**：test `dim_user_all` 常缺行 → 从 prod 同步 success uid 的 dim（organic）再 TASK_ONLY apply。

## 4. TASK_ONLY 补数（仅 apply 示例）

```bash
# schedule = 业务日+1 05:20:00；见 attribution_runbook _complement_test
# API: POST /api/v1/dolphin/complement-data
# task_codes=[21962007716224], task_dep_type=TASK_ONLY, env=test
```

链式 prod 补数：`.claude/database/scripts/attribution_runbook.py complement --start YYYY-MM-DD --end YYYY-MM-DD`（**prod only，须授权**）

## 5. 发布判断

| 环境 | 又初能否自发 | 条件 |
|------|-------------|------|
| test | ✅ | SQL 与 repo 不一致时才 publish-task-sql |
| prod | ❌ | 群 @worker_ant_bot 转知秋；见 `feedback_prod_release_review_gate.md` |

**2026-07-01 状态**：test v76 已与 repo 对齐 → **test 无需再发**；prod 等批复。

## 6. agent-bus 协作

```bash
# ACK（60s 内）
python3 .claude/database/scripts/notify/agent_bus_send.py \
  --to worker_ant --kind ack --reply-to-bus-id N --text "[ACK] bus#N 收到，开干"

# 结案
python3 .claude/database/scripts/notify/agent_bus_send.py \
  --to worker_ant --kind reply --reply-to-bus-id N --text "..."
```

群发帖：`omdb/tgbot/scripts/post_agent_bus_doc_to_group.py` 模式；本机 `urllib` 可能 SSL 失败 → **用 curl** 调 Telegram API。

进度误报「等待执行」→ lesson `2026-07-01-agent-bus-progress-ide-heartbeat.md`

## 7. 关联路径

| 类型 | 路径 |
|------|------|
| result SQL | `ops_system/04.dws/dws.dws_register_attribution_result_d/dws_register_attribution_result_d.sql` |
| apply SQL | `ops_system/06.dim/job_dim_user_attribution_channel_apply/dim_user_attribution_channel_apply_d.sql` |
| 灰度 playbook | `.claude/database/playbooks/dws.dws_register_attribution_gray_verify.md` |
| runbook | `.claude/database/scripts/attribution_runbook.py` |
