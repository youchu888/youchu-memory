---
date: 2026-09-07
tags: [metric-library, G4, G5, write-path, D5]
severity: high
domain: ops
---

# 指标库 G4/G5 写路径门禁已挂 service + API

## 正确做法

- 校验集中在 `dc-platform-server/app/services/metric_gate.py`
- 概念层：`publish_concept` / `set_implementation_primary` 必过门禁
- 旧表：`publish_metric` / batch 必过过渡 G4（formula + binding + agg 白名单 + note 含 `req_ref=`）
- API：`POST /metric-library/concepts/publish`、`POST /metric-library/implementations/set-primary`
- pending promote：先 bind 再 publish（否则 G4_BINDING 必挂）

## 验证

`tests/test_metric_gate.py`；本地无 pytest 时用 importlib/exec smoke。

## 关联

主人定稿 D5=a；lesson 2026-08-29（库内=0 ≠ 应用层已落地）
