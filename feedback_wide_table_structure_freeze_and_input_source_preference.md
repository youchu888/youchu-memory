---
name: wide table structure freeze and source preference
description: For wide-table metadata tasks, only use the user-provided current table structure as source of truth; do not revert to old PDFs; add/adjust only as instructed without deleting/renaming fields.
type: feedback
---
Rule: 宽表任务以用户“当前给出的表结构和说明”为唯一依据；不要再回到旧 PDF 口径。

**Why:** 用户多次强调旧 PDF 已作废且会造成误判；此前因按 PDF 理解导致字段语义和映射说明错误（尤其 create_time 相关）。

**How to apply:**
- 接到宽表任务先锁定“用户最新提供结构”为基线；
- 不删除、不重命名用户给的字段；
- 只做用户明确要求的“补字段、改长度、补来源说明”；
- 公共字段与专有字段语义分开记录：公共 `create_time` 仍是公共字段，同时允许专有事件时间映射字段（如 `order_time <- order_created.create_time`, `pay_time <- order_paid.create_time`）。
