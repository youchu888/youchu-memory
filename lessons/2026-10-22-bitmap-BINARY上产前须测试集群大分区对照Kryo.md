---
date: 2026-10-22
tags: [bitmap, spark, pipeline-runner, datacheck]
severity: high
domain: ops
---

# bitmap BINARY 上产前须在测试集群大分区对照 Kryo

## 背景

`BmUnionAgg` 中间态改 BINARY 可避 Kryo buffer overflow，但每行 deser+ser 整个 bitmap，大分区可能很慢。知秋要求：测试集群大分区对比耗时与结果（须逐字节一致）后再上。

## 正确做法

1. jar 同时注册 `bm_union_binary` / `bm_union_kryo`（见 `BitmapUdf.scala`）
2. 测 `pipeline-runner/testcluster/probe_bitmap_binary_vs_kryo.sh <DT>`（大分区例 login `dt=2026-10-17`）
3. 验收：`card/bytes/sha256` 一致；记录两边 wall / spark elapsed
4. 未出数前禁止把 BINARY 随版本推生产

## 验证

summary JSON 里 `byte_identical=true`，并把 kryo/binary 耗时发狂人。
