---
date: 2026-09-12
tags: [attribution, candidate, enroll]
severity: high
domain: ops
---

# 归因链路关联看候选（同 app 同 IP），不是安装 device JOIN

## 坑

把 V1.0.11 入围新加的 `app_id`+`device_id` 连安装，说成需求里的「同一归因链路」。

## 正确做法

需求里沿用的关联是落地页候选：与注册同 app、同 IP；事件早于注册；时间差不超过 24 小时；channel 非空且不为 organic；分区 T-2 至 T-1。对应结果表 click/view 的 `app_id`+`reg_ip`，不是 `dwd_app_install_d` 的 device_id。

## 验证

`dws_register_attribution_result_d.sql`：`reg_enroll` 连安装；`click_candidates` 连 `dwd_landing_page_click_d`，条件为 `r.app_id = c.app_id AND r.reg_ip = c.ip`，`event_time` 早于注册且 `TIMESTAMPDIFF <= 86400`，`channel` 非空非 organic，`dt` 为 `$[yyyy-MM-dd-2]` 到 `$[yyyy-MM-dd-1]`。
