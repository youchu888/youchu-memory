# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-07-23 · 最新归档：`sessions/tg-rotate-2026-07-23-0818.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- prod 海豚晨检：`get_running_summary` + 当日 `FAILURE` 实例；先判「整 wf 挂」还是「单 task 挂」
- `dws_user_tag_d_d` 在 **`wf_ads_日报表_日`**，不在 `wf_dws_汇总_日`；查失败勿只盯 dws 汇总 wf
- 同 wf 其它 task 全 SUCCESS、仅 1 task FAIL → 优先怀疑该 task 瞬时问题，非全链路/SQL 口径
- 17 秒即 FAIL** 不像 OOM（内存爆通常跑更久）；较像 SR 连接池/内存瞬时竞争
- `fail_retry_times=0` 一次失败即标 wf FAILURE；防复发可设 1~2 次重试，或与最重 ads 任务错开几分钟
- prod Spark/海豚 worker SSH：**`ec2-user@175.41.188.204`**；勿用 `hadoop@IP`；`/etc/hosts` 的 `hadoop-1` 可能指非 prod IP
- TG 问海豚慢（~7min）≠ bot 挂：cursor-agent 在查数，进度提醒默认关，结论仍会 sendMessage
- [LESSON: dolphin,ssh|prod 集群 SSH 用 ec2-user@175.41.188.204，勿用 hadoop@ 或 hosts 里 hadoop-1（可能非 prod IP）]
- [LESSON: dolphin,datacheck|单 task 秒级 FAIL 且补跑成功：先跑验恢复四件套再判瞬时资源问题，不必改 SQL]
- **17 秒即 FAIL** 不像 OOM（内存爆通常跑更久）；较像 SR 连接池/内存瞬时竞争
- 补跑同 SQL 成功 + 上游 DWM 有数 + lifecycle 九档有分布 → 排除口径/上游缺数，数据恢复可结案
- 验恢复四件套：`COUNT(*)` / `max_etl` / 三 DWM 上游行数 / lifecycle 分布
- 平台 `get_task_instance_log` 仅 ~64KB，SR 真错在尾部常被截断；需海豚 UI 翻页或 worker SSH 拉完整 log
- 定位失败点可组合：`ds/full-check` + `list_task_instances` + `failed-tasks` 端点 + prod 查表验数

