---
name: ethan_jobs_filter
description: Ethan 岗位监控筛选规则（大数据/数仓开发 · 禁第三国远程与到岗）
type: feedback
triggers: [岗位监控, ethan-jobs, 招聘筛选, 第三国远程, 到岗]
---

# Ethan 岗位监控筛选规则

## Why

主人 2026-10-07 私聊 #537/#538：岗位筛选只要大数据开发与数据仓库开发相关，不要第三国远程和到岗。

## How to apply

1. 改筛选口径只动 `omdb/tgbot/scripts/ethan_channel_bigdata_jobs.py` 顶部常量（`STRONG_ROLE_MARKERS` / `WEAK_STACK_MARKERS` / `REJECT_LOCATION_RE` / `REMOTE_*`），并在文件头 docstring 同步规则摘要。
2. 岗位本身才算：大数据开发、数据仓库/数仓开发、数据工程师、Spark/Flink/ETL 开发。Kafka、Spark、Hive 这类技术词单独出现不推；「大数据量」不是岗位，裸「大数据」出现在混岗清单里也不推。不要把纯数据分析师、DBA 加回白名单。
3. 地点：默认只留远程/居家；`is_rejected_location` 丢弃第三国远程与到岗（含 `#到岗`）；「无需到岗」否定表述不拦。
4. 改完后须重启 `com.youchu.ethan-jobs-watch`（launchctl kickstart/unload+load）使 KeepAlive 进程加载新脚本。
5. 命中私聊发到 Ethan 号（`ETHAN_JOBS_NOTIFY_USERS`，默认 @ethan223344），不要发到工作号 `ALLOWED_USERS`。
6. 记忆沉淀用本 feedback；勿另起多份冲突规则。
