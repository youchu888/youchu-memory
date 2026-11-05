---
date: 2026-11-03
tags: [shadow-gate, page_item_ctr, ads_page_item_ctr_d, spark_migrate]
severity: high
domain: ops
---

# 点击率首发：全新业务直写正式表（非影子）

## 背景

`ads_page_item_ctr_d` 为首发表；曾误套「影子 7 日闸」。2026-11-05 #12455 纠正。

## 坑 / 错误做法

把「从海豚迁 Spark」的影子双跑规矩套到全新业务上。

## 正确做法

1. 全新业务 → pb 写正式表，不建不写 `*_paimon_shadow`。
2. 细节与全清单见 `2026-11-05-全新业务禁影子直写正式-改回写须扫全清单-bus12455.md`。

## 验证

会话 `sr_use_shadow=false`；pb/`countTable` 无 `_paimon_shadow`。

## 关联

- bus#12455；feedback_new_biz_no_shadow_write_formal.md
