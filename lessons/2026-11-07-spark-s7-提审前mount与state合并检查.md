---
date: 2026-11-07
tags: [spark-migrate, stage7, stage4_spark, mount, request-publish, 野花]
severity: high
domain: ops
---

# Spark S7 提审前：必核 mount；改 state 只合并

## 背景

七张页面/渠道影子提审（bus#12214 批）野花开 Stage7，多会话报「S4 还没挂过调度」。testcluster 已挂；`dev-20261016-008`/`013` 的 `state_json.stage4_spark` 被精简 PUT 冲掉。

## 坑 / 错误做法

- 以为 test 挂过调度就够，不查 state
- `PUT /full` 整份覆盖精简 state，冲掉 `stage4_spark` / s5 / s6 / owned
- 又初在 prod 自建 `*_paimon_shadow`（`sr_prod` 只读，无权限）

## 正确做法

每次 Spark `request-publish` 或请野花走 S7 之前：

1. `GET /full` → 断言 `stage4_spark.mount.ok` 且 `group`/`slot`/`steps` 非空，并与 testcluster 组名一致
2. 断言 `outputs`、`stage4_db_check` 三勾、`stage5_prod_dryrun`、`stage6_commit.sha`
3. 改 state：**先 GET 再合并 PATCH 字段**，禁止精简整份覆盖
4. prod 建影子/正式表 → 野花；又初只提审 + 补 state

mount 丢失修复：从含 mount 的 full 备份合并回 `stage4_spark`（可连带 s4_db/s5/s6），审核人刷新面板后再开 S7。

## 验证

```text
GET full → stage4_spark.mount.ok == true
野花 S7 ① 显示槽位/分组/步名，不再出现「回 S4 第 ③ 步」
```

## 关联

- `2026-11-04-request-publish禁冲owned与先解归档.md`
- `pinned/06-request-publish-owned-archive.md` §35b
- 插件：`vscode-extension/src/views/stage7-spark-panel.ts`（只读 `s4().mount`）
