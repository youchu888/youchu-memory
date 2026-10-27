---
date: 2026-10-27
tags: [spark_migrate, pipeline-runner, S4, full_chain, mgmt-report, attribution, agent-bus]
priority: high
domain: ops
---

# test spark_migrate 挂载通扫：等上游≠缺步；daemon 不回头补缺口格

## 背景

bus#11627（狂人回 #11625）：测试编排挂载清单通扫结论；渠道周/月已卸组；出数卡点与补数计划。

## 通扫快照（2026-10-27）

| 项 | 结论 |
|----|------|
| 卸组 | 09 槽卸掉 `g_ads_channel_promotion_summary_w/m`；组+4 步（含 `pb_`）定义已删 |
| 编排 | 测试机 `full_chain.json` md5=`61dda42c`；daemon **热加载**，不必重启 |
| 挂载 | 清单 11 组 / 26 步已在 04/09/10 槽；SQL 文件在测试机；14 Paimon + 14 SR 目标表均在（**只核存在，未逐列对结构**） |
| 出数 | **都是等上游 / 追平**，不是缺步缺表 |

## 水位 / 卡点（当时）

| 线 | 水位 | 卡在 |
|----|------|------|
| 页面组 / page_heatmap / 渠道日活 | →10-26 | 正常 |
| 渠道日指标 `ads_channel_metrics_daily_d` | 停 10-22 | 等 `dim.dim_user_snap`（测试当时到 10-23） |
| 部门周月 / 产品周月 | 卡 10-21/10-22 | 依赖渠道日指标 |
| `ads_channel_summary_d` | 只跑过 10-19 | 等 `dws_app_channel_summary_d_d`（当时到 10-23） |
| 归因看板 | 停 10-16 | 上游 `dws_register_attribution_result_d` 已到 10-23，但 **10-17+ 不在 daemon 挂账**，不会自己回头补 |
| 无候选原因 | 一格未跑 | 同上，依赖归因 result |
| 产品月 | 仅 seed 的 10-26 | 往后等渠道日指标 |
| `dim_channel_info_all_snap` | 10-19~10-26 齐 | OK |
| `ads_channel_metrics_daily_d` | →10-22 | 同 dim_user_snap |

## 坑 / 错误做法

- 出不了数就当成「没挂上 / 缺表」去补建或重挂
- 以为 daemon 会自动补历史缺口格（未入挂账的日期）
- 狂人 `rerun_*` 还在跑时又起 S4⑤ / 第二份 `rerun.py`
- 因 platform test `sql/deploy` 拉 git **403** 就停补数（SQL 已在测试机时可继续）

## 正确做法

1. **先通扫**：步定义 + SQL 在机 + 表存在；再查水位与上游，区分「缺挂载」vs「等上游」vs「挂账缺口」。
2. **挂账缺口**：上游已齐但格子不在 daemon 挂账 → 用 **`rerun.py` 按依赖顺序补**，daemon 不会自己回头。
3. **补数互斥**：等当前 `rerun_*` 跑完再开下一批；又初配合 **查数**，不抢作业。
4. **本轮狂人补数计划（#11627）**：`rerun_20261027_191301` 完（约北京 10-28 01:00）→ 跑完 10-24 日结/base/dim → 再按序补：归因看板+无候选原因 10-17~10-23（无候选原因先补 10-21 作前一格）、渠道日指标 10-23、渠道汇总 10-20~10-23、部门周/月与产品周 10-22~10-23；更晚由追平后 daemon 接。补完 bus 回清单，又初查数。
5. **卸组后**：勿再把渠道周/月加回测试挂载清单；md5 以狂人最新为准。

## 关联

- bus#11625 / #11627；承接 #11621 S4 自挂与 ≤追平水位
- lesson：`2026-10-27-S4测试五步自挂-禁手改full_chain-补数日不晚于追平水位.md`
