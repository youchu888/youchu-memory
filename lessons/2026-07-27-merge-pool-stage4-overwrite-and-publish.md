---
date: 2026-07-27
tags: [merge_pool, device_tag, stage4, dolphin, overwrite]
severity: medium
domain: ops
---

# merge_pool stage4：同分区多桶 OVERWRITE 会互覆盖

## 坑

`INSERT OVERWRITE ... PARTITION(p{pt})` 按 `bucket_id=0..7` 串行跑时，后一桶会整分区覆盖前桶，验数只剩约 1/8。

## 正确做法

- test / 单 task：默认 `bucket_n=1`
- 多桶：改 UPSERT/先删分区再分桶 INSERT，或拆成互不 OVERWRITE 的目标

## 关联

- session `dev-20260719-001`
- 详情页 `target=null` 须 `s.target?.task_name` 兜底
