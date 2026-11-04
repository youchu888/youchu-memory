---
name: feedback_prod_bucket_from_prod_probe
description: 产发 bucket/并行度只认 prod 探数，禁用 test 行数估配置
type: feedback
---

# 产发 bucket/并行度：只认 prod 探数

**以后怎么做**：凡 fanout / paimon `_r` / Spark 上产涉及 `bucket`、`sinkParallelism`（或同类分桶并行），**先查 prod 量级再填数**。test 行数、test 试跑、口头估计一律不作配置依据。

**错了会怎样**：bucket 建表后改不了；按 test 估小 → 产线打爆或只能删表重建。

**探数最低要求**：

1. prod 上游按业务日 `COUNT(*)`（默认 T-1）
2. 对照现网同量级表在 `fanout/manifest.json` 的 bucket/并行
3. snippet、DDL、design 三处同数，提审写明探数证据

出处：2026-11-04 点击率 pageitem fanout（test 6.4 万 vs prod ~8736 万）。
关联 lesson：`lessons/2026-11-04-产发前探prod量级定bucket并行度禁用test.md`
