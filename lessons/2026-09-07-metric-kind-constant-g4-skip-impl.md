---
date: 2026-09-07
tags: [metric-library, G4, constant, window_days]
severity: high
domain: ops
---

# metric_kind=constant：G4 豁免 active impl

## 背景

Phase2 把 avg 改 derived 时造了 `window_days_7` / `window_days_30` 作分母常数。曾标 `atomic`+`published`，但永远无 `metric_implementation` → 破 G4。bus#8060 知秋给三选一。

## 坑

- 把常数当 `atomic` published → G4 永久告警，门禁被稀释
- `update_time` 是 **concept_code**（现 orphaned），不是 `metric_concept` 列；列名仍是 `updated_at`

## 正确做法（定案 ①）

1. `metric_kind` 增加 **`constant`**（CHECK：`atomic|derived|constant`）
2. G4：`constant` **不要求** ≥1 active impl；仍要 definition + req_ref
3. 血缘：derived 分母继续 FK 引用 constant concept（优于把天数写死进公式）
4. 不新增 lifecycle=`internal`（少状态机）

## 已落地（test metadata 172.31.6.193）

- ALTER DROP/ADD `chk_metric_concept_kind` 含 `constant`
- `window_days_7` / `window_days_30` → `metric_kind=constant`，仍 published
- published+atomic 且 impl=0：**0 条**

## 待平台 API

门禁/升 published 逻辑同步：`metric_kind==constant` 跳过 impl 检查；模型注释已改。

## 关联

- bus#8060 · docs DDL `metric_library_phase0_ddl_v0.3_20260825.sql`
