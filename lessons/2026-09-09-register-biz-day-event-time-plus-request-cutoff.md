---
date: 2026-09-09
tags: [caliber, register, event_time, request_time, biz-day, agent-bus]
severity: high
domain: sql
---

# 注册业务日 = event_time + 两天分区 + request_time 绝对截止线（禁 now）

## 背景

知秋 2026-09-09：用 event_time 须读两天分区；晚到放弃；3 点用 request_time 卡，保证重跑一致。狂人 bus#8332：是 A 但不是裸 A；勿再推产品二选一。

## 坑 / 错误做法

- 只按分区 `dt` 归属（漏跨分区晚到）
- 截止线用 `NOW()` / 跑批时刻 → 重跑不可复现
- 把已定原则再做成 A/B 让产品拍

## 正确做法

1. `DATE(event_time)=业务日`
2. 读 `dt` 与 `dt+1`
3. `request_time < 业务日+1天+3小时`（绝对时刻）
4. 漏斗注册（2026-09-12）：分区仍是入仓日 `dt`（request_time）。只在当天分区加 `event_time ∈ [当天 00:00, 次日 00:00)`（左闭右开）；跨日迟到丢掉，不扫次日分区。截止是次日 0 点，不是 03:00。其它事件仍只按分区 `dt`。

## 验证

跨日样本（如 3 号晚 event、4 号凌晨进仓）应归 3 号且在 4 号 03:00 前纳入；不再进 4 号。

## 关联

- 确认稿：`.claude/database/reports/caliber_register_biz_day/confirm__A_plus_request_time_cutoff__2026-09-09.md`
- bus#8332
