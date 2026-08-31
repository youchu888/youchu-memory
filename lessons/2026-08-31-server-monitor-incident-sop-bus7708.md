---
date: 2026-08-31
tags: [server_monitor, dolphin, incident, prod, download-log, dependent]
severity: high
domain: ops
---

# server_monitor 告警处置：先验仍在发生、禁信根因字段、DEPENDENT 是果

## 背景

bus#7708 狂人 SOP 请示回执（知秋盯 prod dwd 大表拆分）；完整 SOP 晚些补，先定四条避免卡 playbook。

## 坑 / 错误做法

1. **test 告警当 prod 事故** — test 断流/不新鲜/僵尸 wf 是已知噪声
2. **跳过「此刻还在发生吗」直接判因** — 最近实例已 SUCCESS 仍是延迟播报，继续追因白烧 token
3. **顺着 DEPENDENT「等_*」往下追** — 成批 DEP 失败是果，真因在某一个 SQL task
4. **引用 server_monitor「根因」字段** — 规则猜测；KILL 被误报成分区幂等，真日志是 client request cancel
5. **用 `/log/detail` 判因** — 截断前几百行，误判「日志无报错」
6. **本地直连 prod 写操作或重复造监控** — 补数/complement/publish 须请示；检测已在 54.255.236.159 monitor 脚本

## 正确做法

1. 只看 **env=prod**；test 噪声忽略
2. FAIL 前第一步：查最近 N 次实例 state；最近 SUCCESS → **延迟播报收工**
3. DEPENDENT 批量 FAIL → 找真失败 SQL task
4. 日志：`GET /log/download-log?taskInstanceId=<ti>`；禁 `/log/detail`
5. prod 海豚仅 GET 直连；写操作与补数灰区先请示知秋
6. 真人 executor 手动 RUNNING → 不当事故（如今日 paimon_history_clean_controller 千行调试）

## 验证

- playbook：`.claude/database/playbooks/_ops_server_monitor_incident.md`
- 下次 server_monitor 告警按 part_01→04 顺序，不跳步

## 关联

- bus#7708
- `_ops_dolphinscheduler_workflow_update.md`
