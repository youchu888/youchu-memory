---
date: 2026-10-13
tags: [ethan-jobs-watch, 岗位监控, 大数据]
severity: medium
domain: ops
---

# 岗位监控必须命中岗位本身，技术栈顺带出现不算

## 背景

2026-10-13 初儿把 Go 代码审计、Golang 开发推成「大数据/数仓开发」。一条正文是「大数据量」，一条只提到 Kafka。

## 坑 / 错误做法

`大数据` 子串命中「大数据量」；Kafka / Spark / Hive / ETL 单独出现也当岗位。混岗清单里列了「大数据」同样被推。

## 正确做法

`is_job_like` 只认 `STRONG_ROLE_MARKERS`（大数据开发、数仓、数据工程师、Spark/Flink/ETL 开发）。`WEAK_STACK_MARKERS` 单独命中不推。规则写在 `feedback_ethan_jobs_filter.md`。改完 `launchctl kickstart -k gui/$(id -u)/com.youchu.ethan-jobs-watch`。

## 验证

本地样例：Go + 大数据量 + Kafka、代码审计 + Kafka、混岗清单「大数据」均为 false；「大数据开发 / 离线数仓」「数据仓库开发」「Spark 开发」为 true。

## 关联

- 脚本：`omdb/tgbot/scripts/ethan_channel_bigdata_jobs.py`
- 规则：`~/.dc-platform/memory/feedback_ethan_jobs_filter.md`
