# server_monitor / prod 海豚告警处置 SOP

> **执行主机**：**old-mac 专责**（tgbot / monitor 告警入口在权威机；new-mac 不另建夜间巡检）  
> **权威来源**：bus#7708（狂人阶段性回执，2026-08-31）  
> **完整版 SOP**：狂人晚些补（又初 bus#7706 追问中）  
> **本机副本**：`~/.dc-platform/memory/playbook_server_monitor_incident.md`（双机 memory sync）  
> **工作区副本**（gitignore）：`CHcode/.claude/database/playbooks/_ops_server_monitor_incident.md`  
> **关联**：lesson `2026-08-31-server-monitor-incident-sop-bus7708.md`

## 0. 适用范围

| 项 | 约定 |
|---|---|
| **触发** | `server_monitor`（`54.255.236.159` / `prod_monitor/server_tick.py`）推 TG 或 agent-bus 的 prod 海豚告警 |
| **不负责** | 另建本机「每晚全量扫海豚」定时任务（检测已在服务端 monitor 脚本） |
| **环境** | **仅 prod**；test 断流 / 不新鲜 / 僵尸 wf 为已知噪声，**忽略** |
| **写操作** | prod 补数 / complement / publish / 改 SQL → **灰区，先请示知秋或 bus 狂人**（bus#861） |
| **prod 海豚通道** | 诊断：**平台 MCP/API 或 GET 直连**；禁止本地私自发 prod 写操作 |

## 1. 硬规则（处置前必读）

1. **先验「此刻还在发生吗」** — 最近实例已 SUCCESS → 延迟播报收工，禁止继续追根因。
2. **DEPENDENT 批量 FAIL 是果** — 找第一个真失败的 **SQL task**，勿顺着 `等_*` 链往下追。
3. **禁信 server_monitor「根因」字段** — 规则猜测；例：KILL 被误报成分区幂等，真日志常为 `client request cancel`。
4. **日志必须用 download-log** — `GET /log/download-log?taskInstanceId=<ti>`；**禁止** `/log/detail`（截断前几百行）。
5. **真人 executor 手动 RUNNING** — 不当事故（例：`paimon_history_clean_controller` 千行调试）。
6. **test 告警 ≠ prod 事故** — 只看 `env=prod` 推送。

## 2. 处置 parts（按序，不跳步）

### part_01_still_failing — 是否仍在失败

**输入**：告警中的 `project_code` / `wf_code` / `process_instance_id`（或 wf 名 + 业务日）

**动作**（平台 MCP 优先）：

```text
dolphin_list_process_instances(env=prod, project_code=..., wf_code=..., limit=5)
```

**判定**：

| 结果 | 结论 | 下一步 |
|---|---|---|
| 最近 1～3 次实例 state = SUCCESS | **延迟播报** | part_04 写报告「已自愈」，**收工** |
| 最近实例 FAIL / KILL / STOP | 仍在发生 | → part_02 |
| RUNNING 且告警为「长跑」 | 查是否真人调试 | 真人 executor 手动跑 → **收工**；否则 → part_02 |

**期望**：明确「收工」或「继续 part_02」。

---

### part_02_find_root_sql_task — 定位真失败 SQL task

**动作**：

1. 对 FAIL 的 `process_instance_id`：
   ```text
   dolphin_list_task_instances(env=prod, project_code=..., process_instance_id=...)
   ```
2. 若成批 **DEPENDENT**（`等_*`）FAIL：
   - **不要**逐个 DEP 往下追
   - 找列表中第一个 **SQL / SHELL / SPARK** 且 state = FAILURE 的 task
   - 服务端 monitor 已有 `resolve_dependent_root`（`prod_monitor/probe_ds_rest.py`），可对齐其输出
3. 记录：`task_code` / `task_instance_id` / task 名 / `host` / `duration`

**判定**：

| 结果 | 结论 |
|---|---|
| 找到唯一 FAILURE 的 SQL 类 task | PASS → part_03 |
| 仅 DEPENDENT 失败、无 SQL FAILURE | WARN → 扩大窗口查上游 wf 或上一周期 pi |
| 多个 SQL 同时 FAIL | WARN → 按 DAG 拓扑找最上游 FAILURE |

---

### part_03_download_log — 拉全量日志判因

**动作**（禁 `/log/detail`）：

```text
# 平台 MCP（若封装 download-log）
dolphin_get_task_instance_log(env=prod, task_instance_id=<ti>, mode=download)

# 或 DS REST（prod GET only）
GET /log/download-log?taskInstanceId=<ti>
```

**读日志要点**：

- SQLException / 列错位 / 分区不存在 / OOM / cancel
- **忽略** monitor 推送的 `root_cause` 文本，以日志为准
- KILL：区分「分区幂等重跑」误报 vs `client request cancel` / 人工 kill

**判定**：

| 结果 | 结论 | 下一步 |
|---|---|---|
| 根因明确且属「只读/重跑可修」灰区 | 记录根因 | → part_04 + bus 狂人请示 |
| 根因 = SQL/口径/发布问题 | 需改代码或 publish | **禁止私自发 prod** → bus 狂人 + 走 dev session |
| 日志空 / 截断 | FAIL | 确认用的是 download-log 而非 detail |

---

### part_04_report_and_escalate — 报告与升级

**报告路径**：`.claude/database/reports/_ops_server_monitor/<dt>/incident__<wf>__<timestamp>.md`

**报告模板**：

```markdown
# server_monitor 告警处置 · YYYY-MM-DD HH:MM

## 结论
[延迟播报已收工 | 已定位待修 | 需请示]

## 告警摘要
- env: prod
- wf / task / pi / ti
- monitor 推送时间

## part_01 仍在发生？
[最近实例 state 列表]

## part_02 真失败 task
[task 名 / ti / code]

## part_03 日志根因
[1～3 句，附关键 log 行]

## 建议动作
- [ ] 无需动作（延迟播报）
- [ ] 请示后 complement / 重跑（写清楚 dt、task、理由）
- [ ] 需 publish / 改 SQL → dev session

## 未决（等狂人完整 SOP）
- 可直接修白名单 / 每晚窗口 / wf 清单
```

**升级通道**：

| 场景 | 通道 |
|---|---|
| 需补数 / 重跑 / 杀僵尸 | agent-bus → worker_ant（附 part_03 证据） |
| 需 prod publish / 改 SQL | bus 狂人 + 知秋令 + 开发平台 session |
| 仅告知已自愈 | TG 私聊主人一行 或 静默（无事不刷屏，等狂人完整 SOP 拍板） |

## 3. 与现有 monitor 的分工

| 组件 | 位置 | 职责 |
|---|---|---|
| `server_tick.py` | `54.255.236.159` | 每分钟 tick；每小时 :30 后 DS REST 探 fail + 长跑；09:30  morning_data_check |
| `probe_ds_rest.py` | 同上 | fail task 列表、DEP root 解析、stderr tail |
| `task_partition_check.py` | 同上 | 任务 SUCCESS 后 10min 查分区空/滞后/量跌 |
| **又初** | Cursor / IDE | 收到告警后按本 playbook part_01→04 处置；**不重复造监控** |

## 4. 禁止事项

- ❌ test 告警当 prod 事故处理
- ❌ 跳过 part_01 直接追根因
- ❌ 引用 monitor `root_cause` 字段作为结论
- ❌ 使用 `/log/detail` 判因
- ❌ 本地直连 prod 做 complement / publish / PUT workflow（bus#861）
- ❌ 在本机 old-mac/new-mac 另建「每晚全量扫海豚」cron

## 5. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-31 | 初版：自 bus#7708 沉淀 part_01～04；完整 SOP（窗口/白名单/可直接修清单）待狂人补 |
