---
date: 2026-08-10
tags: [datacheck, full-chain, dws, reconstruct, playbook]
severity: high
domain: datacheck
---

# DWS 核查须从上游按 ETL 规则全量重算交叉，禁止只抽单表

## 背景

主人要求对又初名下数据做多角度核查：从 DW/DWM 起按规则临时重算，与落表全量交叉比对，并沉淀经验。页面访问、停留五档在 `dt=2026-08-09` prod 跑通。

## 坑 / 错误做法

- 只查单表 TOP N / 分区行数，宣称「有数即 OK」
- 发现 `pv=0 AND jump>0`、某 app DWS 近空就判 ETL 丢数，未回溯过滤口径
- VPN 过期时仍连 FE（TCP 通但握手超时），误判库挂

## 正确做法

1. **先画链路**：目标表 ← 上游事实表；把 ETL 过滤/CASE 抄成临时 `WITH recon`
2. **两层对账**：汇总 diff（全指标）+ 主键 FULL OUTER JOIN（match / only / mismatch）
3. **旁证同域表**（click / 上游键集覆盖），区分「设计内」与「真错数」
4. 查库前确认 VPN（握手能收到 MySQL greeting）；过期跑 `vpn_ovpn_sync.py`

页面访问脚本：`.claude/database/reports/dws.dws_app_page_visit_d_d/_run_full_chain_check.py`  
全链路脚本：`.claude/database/reports/youchu_full_chain/_run_all_chains.py`

## 验证

- visit：862344 行 match，汇总 diff=0
- session_duration session/daily：行数与 session_cnt/user_cnt/dur 汇总 diff=0；行级 91354 match

## 关联

- 报告：`reports/dws.dws_app_page_visit_d_d/validate__2026-08-09__20260810_191038.md`
- 报告：`reports/youchu_full_chain/validate_all__2026-08-09__20260810_191802.md`
- playbook：`ops_system/04.dws/dws_app_page_visit_d_d/playbook.md` part_04/05
