---
date: 2026-08-17
tags: [metric-library, bus-6552, session-rotate, self-evolve]
severity: high
domain: ops
---

# 指标库 #6552：区分「认可(v0.1既有)」与「评审新增三处必改」，published 四件套含 req_ref

## 背景

bus#6622 口头摘要把 v0.1 §8 的「AI 只 propose / 改口径升版」误记成知秋新增的 H2/H3 门槛，同时漏了 req_ref、禁比率、aggregation 白名单。bus#6625 纠正。

## 正确做法

引用 #6552 时严格分两层：

1. **认可栏（v0.1 既有，非新门槛）**：不做 Headless BI；AI 只 propose；改口径升版。
2. **评审新增三处必改 (a)(b)(c)**：
   - (a) published 硬门槛补 **req_ref 非空**（与 definition + binding + 合规 aggregation 合称**四件套**）
   - (b) **禁比率进 canonical**；`derived` 强制 numerator + denominator
   - (c) **aggregation 白名单**；UV 强制 `bitmap_union_count`

另有两坑（别名 NULL 唯一键、is_primary 顺序）见 `docs/metric_library_system_v0.2_20260815.md` §5–§6。

**禁止**把「三处硬门槛」说成 H1=definition、H2=AI propose、H3=升版。

## 验证

`docs/metric_library_system_v0.2_20260815.md` §1 / §1b / §2 与 #6552 全文逐条可对齐。

## 关联

- 设计稿：`docs/metric_library_system_v0.2_20260815.md`
- bus#6552 评审回应、bus#6625 纠正
