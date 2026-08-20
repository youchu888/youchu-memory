---
date: 2026-08-20
tags: [spark, yarn, user-tag, wrapper_daily_v3, etl_state, bus6901]
severity: high
domain: ops
---

# Spark prod 可用；用户标签链必须走 wrapper_daily_v3，禁手工逐步跑

## 背景

bus#6901（2026-08-20，狂人实查）：prod 集群 Spark/YARN 可用，并交底用户标签日链运维红线。

## 坑 / 错误做法

- 手工逐步跑 `dws_user_tag_base_d_d_v3` 及后续步：不提交 `etl_state` 水位 → 下次 wrapper 再累加 → **累计列翻倍**
- 标签链放 0 点与结算抢资源
- 把「Spark 环境可用」当成「prod 分区可上」的授权（分区上线须知秋拍板）

## 正确做法

1. **集群**：prod `hadoop-1`；Spark `/opt/bigdata/spark`；提交 `--master yarn --deploy-mode client`。2026-08-20 03:57 已跑通 dt=2026-08-15 全链（天链→小时框架→结算）。test 侧未查，要 test 须另说。
2. **余量**：YARN default 占用约 37% 时可提交不排队；常态含 7 个 Flink 常驻 + `spark_thriftserver_prod`。
3. **标签链**：五步 ad/video/base/tag/dim 约 720s；**必须** `ops_system/00.pipeline/user_daily_backfill/wrapper_daily_v3.sh <dt>`。base（`dws_user_tag_base_d_d_v3`）起不幂等，累计列 sum 增量，靠 `etl_state.sh` 水位闸门。
4. **错峰**：标签链按现行设计约 **03:10** 起跑，勿放 0 点。
5. **dim 余量**：`dim.dim_user_all_d` 唯一下游是次日 01:03 日间表，约 21h 余量，不必赶。
6. **prod 分区上线**：知秋拍板；狂人只确认环境可用与验数可跑。

## 验证

- 日更只经 wrapper；查 `etl_state` 水位与目标 dt 一致
- 禁止手搓逐步跑后再让 wrapper 重跑同 dt

## 关联

- bus#6901
- 脚本：`ops_system/00.pipeline/user_daily_backfill/wrapper_daily_v3.sh`、`etl_state.sh`
