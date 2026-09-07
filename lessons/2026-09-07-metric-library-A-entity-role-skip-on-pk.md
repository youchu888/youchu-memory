---
date: 2026-09-07
tags: [metric-library, prod-sync, entity_dict, role_dict, phase-A]
severity: high
domain: ops
---

# 指标库 A 灌包：entity_dict/role_dict 主键全撞 → 只 skip 不覆盖

## 背景

bus#8066：prod 概念层 6 主表 0 行（纯新增），但 entity_dict=4 / role_dict=5 已有 Phase0 种子。清单漏报这两张会假称「纯新增」。

## 正确做法

1. A 包必须带 **test vs prod**（或 vs Phase0 seed 基线）entity/role PK diff。
2. 撞车策略：**INSERT 遇 PK 存在则 skip**；**禁止**对这两张表 `ON DUPLICATE KEY UPDATE`。
3. 其余 6 张空表才可纯 INSERT。
4. 平台 `prod_sync` / OpenMetadata 同步 **不管** metadata 这 8 张表 → 只能手工灌包。
5. 本机/test 堡垒常 **达不到** prod RDS `dc-data.*.rds.amazonaws.com:3306`；prod 行级 diff 优先让能连 prod 的人验，或对照 08-26 seed 回执。

## 关联

- bus#8066 · Phase0 seed `docs/metric_library_phase0_seed_entity_role_20260825.sql`
