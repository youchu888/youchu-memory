---
date: 2026-09-07
tags: [metric-library, ui, concept-detail, 知秋]
severity: high
domain: ops
---

# 概念指标详情必须一路展开（label + impl + 关系图）

## 背景

bus#8082 知秋打回 test 概念层界面：数据层 OK，详情页只有 kv 断了。

## 正确做法

1. 详情四段：是什么 / 怎么叫(labels) / 在哪实现(impls，主实现醒目) / derived 分子分母
2. 所有 code 可点：实体、事件、concept、table_fqn→`/tables/{db}/{table}`
3. 关系图画 **SVG 白底浅色**，禁深色主题
4. 菜单「事件扩」→「事件归属」；tab=`概念指标|标准指标|实体 角色 事件归属|审核`；默认进概念指标
5. `/metrics/concept` 会被 `/metrics/{name}` 抢路由 → 在 ui_metrics 对 `name==concept` 做 303 到 concepts
6. test 重启必须用 `/web/metadata/start_test.sh`（勿裸 uvicorn，缺 SESSION_SECRET）

## 关联

- bus#8082
