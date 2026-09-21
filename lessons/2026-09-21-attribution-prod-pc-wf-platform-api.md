---
date: 2026-09-21
tags: [attribution, complement, dolphin, runbook, funnel]
severity: high
domain: ops
---

# 归因 prod 补数须用运营系统真 PC/WF；直连海豚常 404

## 背景

本月补跑归因升级时，`attribution_runbook.py` 仍写测试环境 code（`PC=205248…`），直连 `.claude/dolphinscheduler.json` 的 prod host 对 `/projects` 一律 404。

## 坑 / 错误做法

- 用 runbook 旧 PC/WF/`metrics_d_d` task code 直连 `DolphinClient("prod")`
- 当「时间漏洞」理解成别的表；口语实指**事件漏斗**（大漏斗）
- 大漏斗用 `full_chain` 整链 catchUp（会拖进小时链）

## 正确做法

- prod：**运营系统** `PC=171982119739200` · `WF=174729604091712`（`wf_dws_汇总_日`）
- 链：`result_d(174729603403591)` → `channel_apply(176496005400704)` → `is_run_sync(183734415214720)`；看板/无候选可另补。prod **无** `metrics_d_d` task
- schedule：业务日 D → `[D+1 05:25, end+2 05:25)`（对齐 crontab `0 25 5`）
- 补数入口：dc-platform `dolphin_complement_data` / runbook（已改走 platform API）
- 大漏斗：`pipeline-runner/steps/funnel_backfill.json` +  
  `bash run_daemon.sh --steps=.../funnel_backfill.json --from=2026-09-02T06 --until=2026-09-21T06`  
  （槽位 06、unit=day → 业务日 09-01～09-20）；需 VPN 连 `ec2-user@175.41.188.204`

## 验证

- `dolphin_get_running_summary` idle；instance `COMPLEMENT_DATA` SUCCESS
- SR：`created_at` / 行数按日抽查（需能连 `sr_prod`）

## 关联

- 脚本：`.claude/database/scripts/attribution_runbook.py`
- 步骤：`pipeline-runner/steps/funnel_backfill.json`
