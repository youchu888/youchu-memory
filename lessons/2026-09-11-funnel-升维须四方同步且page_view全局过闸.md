---
date: 2026-09-11
tags: [funnel, pushback, SR, sandbox, datacheck, agent-bus]
priority: high
domain: etl
---

# 大漏斗升维：SR 回写表须四方同步；page_view HAVING 须全局过闸

## 背景

bus#8357：今晚升维未上线；生产 SQL 已回滚。沙箱对账仅 `app_page_view` 负差拦上线。

## 坑 / 错误做法

- 只改 paimon `spark_sql`，不改 SR 正式表 / pushback → 回写挂或列对不上
- `page_qual_uid` 把 `device_type`/`source_type` 写进 `GROUP BY`+`HAVING` → 细粒度过闸丢用户，可加指标 `event_cnt` 加总回退出现负差

## 正确做法

1. **四方同次到位**（知秋）：`spark_sql` + paimon 目标表 + **SR 正式表结构** + **pushback SQL**；缺一 → 回滚 SQL、当晚不上线
2. **`app_page_view` 入围**：同一 uid 当日 `page_key` 去重 >1；过闸粒度 = `(dt,app_id,uid)`；过闸后再按 device/source 拆维计数
3. 升维对账：键对齐 + 可加指标 SUM 回退精确相等；`*_session_cnt` 拆维后小幅正差可接受

## 验证

- prod SR `DESC` 含 `device_type`/`source_type` 且 pushback `grep device_type`>0
- 沙箱 09-08 加总回退：`app_page_view` 的 user/event 无负差

## 关联

- bus#8357；备份 `hadoop-1:.../sql_youchu_new_20260910/`
- lesson：`2026-09-10-funnel-升维验收须runner-test禁SR手工灌数冒充.md`
