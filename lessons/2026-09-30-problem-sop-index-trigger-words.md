---
date: 2026-09-30
tags: [sop, pipeline-runner, settlement, dim_user, spark, agent-bus]
severity: high
domain: ops
---

# 问题处置 SOP：按触发词对号入座，勿从零查

## 背景

狂人 bus#9470（知秋令发索引）：五份 SOP 入仓 `dc-parent` `dev @1c752986`。遇事先对触发词，照清单做。

## 正确做法

| # | 路径（dc-parent） | 触发词 |
|---|------------------|--------|
| ① | `docs/sop_settlement_stall_backfill.md` | 结算断流 / dws_settlement_detail 不新鲜 / 扣量小时表缺格 / 探针等结算 / 挂账堆积 |
| ② | `docs/sop_dim_user_snap_repair.md` | dim_user_snap / dim_user_all_d_v 读不到数 / 用户全表行数不对 |
| ③ | `docs/sop_user_space_late_arrival_verify_and_backfill.md` | 用户空间 / 事件迟到 / dwd 比值不对 / 页面浏览缺数 |
| ④ | `docs/sop_mount_new_step_to_pipeline_runner.md` | 挂新步 / 进 full_chain / 上调度 |
| ⑤ | `docs/runner_12_groups_normal_shape.md` | runner 某组是不是挂了 / 步数对不对 |

CHcode 已有副本：`docs/sop_mount_new_step_to_pipeline_runner.md`（④）。

### 五条通用铁律（摘要）

1. 海豚 state=7 仍可能空跑：看耗时骤降（7–8s→0–1s）+ 分区是否真有
2. 挂账缺 resolved ≠ 未做：看 HDFS `state/pipeline_runner/<日>#<槽>/<step>.json`
3. 时区三套：本机东京 / 日志北京 / hadoop-1 UTC；先 `date -u`
4. Spark `SELECT assert_true` 假绿：包 `CACHE TABLE ... AS SELECT assert_true(...)`
5. 回写 SR 按字节量长：用 `OCTET_LENGTH`，勿用 Spark `LENGTH` 当 varchar 上限

结算断流：`MAX(event_time)` 必须带时间过滤；勿停 pipeline-runner daemon。  
挂新步：先沙箱落 test.* 对账，再动 `full_chain.json`。

## 关联

- bus#9470
- 仓：dc-parent `dev` @1c752986
