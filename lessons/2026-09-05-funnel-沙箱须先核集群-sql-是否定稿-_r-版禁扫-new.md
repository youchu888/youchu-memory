# 大漏斗沙箱：开跑前必须核对集群 SQL 是否定稿 _r 版

- **tags**: funnel, sandbox, hadoop-1, pipeline-runner, dwd_r
- **date**: 2026-09-05
- **source**: bus#8006 / bus#7916

## 坑

git 上已是 `563013e7` 全切 `dwd.*_r`，但 hadoop-1 `/home/ec2-user/pipeline-runner/sql/dws_app_event_funnel_d_d_daily_stage_metrics.sql` 仍可能是改造前旧版（三次扫 `dw.dw_user_event_detail_new` → 1.9TB / 1.5万 splits / 数小时卡死）。

## 正确做法

1. 开跑前 `wc -c` + `grep FROM` 核远程 SQL；与本地 md5/`563013e7` 对齐后再 `run_test.sh`
2. `sdk_init` 读湖表 `paimon.dwd.dwd_sdk_init_d_r`（不是 SR `dwd_sdk_init_d`）
3. 起沙箱前 bus 告知狂人，避免 `pkill -f com.dc.pipeline.Main` 误伤（沙箱与生产同主类）
