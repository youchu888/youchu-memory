---
date: 2026-08-10
tags: [page-visit, jump_only, empty-uid, caliber, datacheck]
severity: high
domain: datacheck
---

# 页面访问：jump_only 与空 uid 大盘是口径规律，不是 ETL 丢数

## 背景

`dws_app_page_visit_d_d` 与 DWD 全量重算一致后，仍见大量 `pv=0 AND jump_cnt>0`，以及 TJ/DX 等 app「DWD view 巨大、DWS 近空」。

## 坑 / 错误做法

- 把 jump_only 行当脏数据去「修」ETL
- 把空 uid 过滤后的近空 app 报成 visit 任务失败

## 正确做法

| 现象 | 解释 | 开发注意 |
|------|------|----------|
| jump_only | `page_keys = view ∪ jump ∪ stay`；referrer 当日未作浏览目标仍计跳转源 | UNION 设计保留；看板勿把 jump_only 当 PV 页 |
| 空 uid | 账号口径丢 `uid` 空行；部分 app empty_uid≈100% | 对账用「有 uid 的 view」≠ raw view |
| view 行数 = stay 行数 = DWS.pv | 过滤后 1:1 | 可作为健康探针 |

T-1=2026-08-09：jump_only≈546689/862344；TJ-001/TJ-003 等 empty≈100%。

## 验证

DWD 规则重算与 DWS 行级全 match 后，再解释规律；勿先改 SQL。

## 关联

- `ops_system/04.dws/dws_app_page_visit_d_d/dws_app_page_visit_d_d.sql`
- lesson：`2026-08-10-dws-full-chain-reconstruct-crosscheck.md`
