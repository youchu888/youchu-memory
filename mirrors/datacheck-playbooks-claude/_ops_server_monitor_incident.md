# server_monitor 告警处置 SOP

适用：收到 `server_monitor` / prod 海豚 FAIL 类告警后的**处置**（不是再建检测）。

来源：bus#7708 + bus#7742；主人 2026-09-01 确认按狂人安排执行。权威全文见 `~/.dc-platform/memory/playbook_server_monitor_incident.md`。

## 0. 边界

| 项 | 规则 |
|---|---|
| 监控范围 | **只看 env=prod** |
| test 噪声 | env=test 的「数据不新鲜 / 断流 / 僵尸 wf」**一律不处理**，不写进处置分支 |
| 检测 vs 处置 | `server_monitor` 已在 `54.255.236.159:/data/dcpaltform/monitor/` 跑全量核查；又初做**处置**不重复检测、不另建夜间全量扫 |
| 写操作·事故 | 六条判据确认 prod 事故 → **立刻修（含改代码）**，修完再报（#7742） |
| 写操作·非事故 | 日常变更 / 口径 / 设计加表 → 仍等知秋 GO |
| 手动调试 | executor 为真人且最新实例 RUNNING → 先认「有人在手动跑」，不当事故处置 |

## 1. 处置流程（硬顺序）

### part_01 此刻还在发生吗（先于一切判因）

1. 查该 task **最近 N 次**实例 `state`（MCP `dolphin.list_task_instances` 或 DS GET）
2. **最近一次 = SUCCESS** → 定性 **延迟播报**，收工；禁止继续追「为什么发生」
3. 告警晚于故障闭环非常常见；跳过本步会在已闭环问题上白烧 token

### part_02 找真因 task（别追 DEPENDENT）

1. 「等_*」等 DEPENDENT 节点成批失败 = **果不是因**
2. 去找那一个真正失败的 **SQL task**；禁止顺着 DEPENDENT 链往下追

### part_03 取证（禁信 monitor 根因字段）

1. `server_monitor` 报的「根因」= 规则匹配猜测，**不可直接引用**
2. 真实日志只用：`GET /log/download-log?taskInstanceId=<ti>`
3. **禁止**用 `/log/detail` 判因——截断在前几百行，错误行看不到，易误判「日志无报错」
4. 典型误判：KILL 任务被猜成「分区已存在」；真日志常为 `Statement cancelled due to client request`

### part_04 修复与升级

1. 确认仍 FAIL 且非延迟播报、非手动调试后，按 `_ops_dolphinscheduler_workflow_update.md` 边界操作
2. prod 写操作、补数范围、级联下游 → 先请示知秋 / 狂人，禁止自行起头
3. 级联下游 wf 须纳入复原计划（见 lesson `2026-07-02-result-cascade`）

## 2. 判定速查

| 现象 | 定性 | 动作 |
|---|---|---|
| test env 断流/不新鲜 | 已知噪声 | 忽略 |
| 最近实例 SUCCESS | 延迟播报 | 收工 |
| 批量「等_*」FAIL | DEPENDENT 级联 | 找上游真失败 SQL task |
| monitor 根因 vs download-log 不一致 | 误判 | 以 download-log 为准 |
| FAILURE + 真人 executor RUNNING | 手动调试 | 观察，不当事故 |
| 需 publish / complement prod | 灰区 | 请示知秋 |

## 3. 变更记录

| 日期 | 变更 |
|---|---|
| 2026-08-31 | 初版：bus#7708 四条 SOP（监控范围 / 取证 / 修复边界 / 别重复造监控） |
