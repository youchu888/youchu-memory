---
name: feedback_new_biz_no_shadow_write_formal
description: 全新业务禁影子双跑；改 pb 目标须扫全清单，禁止只改两份 SQL
type: feedback
---

# 全新业务 · 直写正式表 · 改回写扫全清单

## 规矩

1. **全新业务**（SR 无旧海豚写方可对、或正式表本为空壳新建）：**不走** `*_paimon_shadow` 双跑；pb 直写正式表。
2. **「先写影子 7 日对平再切正式」** 只适用于 **从海豚迁到 Spark 的升级表**（现网正式表仍有读者/写者）。
3. 会话 `sr_use_shadow` 必须与真实回写一致；全新业务应为 `false`。
4. 改回写目标时 **禁止只改两份 `pb_*.sql`**，必须同批核对下面清单。

## 改「影子→正式」自检清单

- [ ] `pb_*.sql` 的 `INSERT OVERWRITE` 表名
- [ ] `step.json` 里 pb 的 `countTable` + 中文名/简介
- [ ] `task.yaml` `downstream`
- [ ] 会话 `sr_use_shadow` / `sr_target_table` / outputs（勿登记影子 DDL）
- [ ] `design.md` / `对接_表结构.md` 现行口径（调度段、回写段）
- [ ] 删除或停用仓内 `*_paimon_shadow_ddl.sql`（避免 S4/S7 误建）
- [ ] `pipeline-runner/testcluster/full_chain_testcluster.json`（及 prod 编排若已挂）同名步 `countTable`
- [ ] playbook 核查对象改正式表；旧「影子闸」段标明已废

## 反例（已踩）

- 点击率 `ads_page_item_ctr_d`：#12440 仍按影子 7 日闸；#12455 定全新业务直写正式后，只改 pb 不够——`design` 调度段、影子 DDL、testcluster `countTable` 仍残留影子。

## 关联

- lesson：`lessons/2026-11-05-全新业务禁影子直写正式-改回写须扫全清单-bus12455.md`
- 红线：`pinned/07-new-biz-no-shadow-formal.md` §36
- 点击率会话：`ops_system/spark_migrate/ads_page_item_ctr_d/`


归类入口：[`playbook_spark_prod_publish.md`](playbook_spark_prod_publish.md)
