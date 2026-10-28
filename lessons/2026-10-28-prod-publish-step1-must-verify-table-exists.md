---
date: 2026-10-28
tags: [prod-publish, stage7, ddl, refresh-prod-built]
severity: high
domain: ops
---

# Stage7 Step1 勾 DDL 必须先查 prod 实表，禁止只靠 checkbox

## 背景

`dev-20261027-001`（产品推广月表）发布向导 Step1 勾了 `ads.ads_product_promotion_summary_m`，后续 Step 继续走完，但 prod 只有周表 `_w`、没有月表 `_m`；`outputs[].prod_table_built=false`，`publish_runs=[]`。

## 坑 / 错误做法

- wizard 勾选只写 `prod_publish_steps.step1.ddls[fqn]=true`，不校验 information_schema
- 勾后虽调 `refresh-prod-built`，缺表只 `console.warn`，不回滚勾选、不拦解锁
- 「完成发布」也不查表，可在未建表时写 PublishRun / 标 stage7

## 正确做法

1. **勾选前门禁（插件）**：`ddl-toggle` checked → 先 `refreshProdBuilt`；该 fqn 在 `missing_tables` 或所在库查失败 → `ddl-reject` 回滚勾选 + 报错，不落盘 true
2. **完成发布前门禁（插件 + 服务端）**：Step6 / `POST /prod-publish/{code}/complete` 对 body.fqns 再查 prod；缺表 **409**，查库失败 **502**
3. **真值**：badge / 列表只认 `outputs[].prod_table_built`（`refresh-prod-built` 写回），不认 checkbox 口述
4. **本机 readonly**：本地 `my.cnf.prod` / MCP `sr_prod` 只读，建表须有写权限账号在 prod 命令行执行 DDL 后，再勾 / refresh

## 验证

```bash
# 缺表应出现在 missing_tables
POST /api/v1/dev-sessions/<code>/refresh-prod-built

# 缺表完成发布应 409
POST /api/v1/prod-publish/<code>/complete  body.fqns=[缺表fqn]
```

prod：`ads.ads_product_promotion_summary_m` 建成后 refresh → `prod_table_built=true`，才允许勾 Step1 / 完成发布。

## 关联

- 插件：`vscode-extension/src/views/prod-publish-wizard.ts`
- 服务端：`dc-platform-server/app/routers/api_v1_prod_publish.py`（`_prod_tables_missing`）
- session：`dev-20261027-001`（假勾已清空；表仍待 prod CREATE）
