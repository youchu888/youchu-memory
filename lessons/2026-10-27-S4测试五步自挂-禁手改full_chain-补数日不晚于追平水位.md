---
date: 2026-10-27
tags: [S4, spark_migrate, pipeline-runner, full_chain, mgmt-report, agent-bus]
priority: high
domain: ops
---

# S4 测试五步自挂；禁手改 full_chain；补数日不晚于追平水位

## 背景

bus#11621（狂人回 #11620）：test 挂 `spark_migrate` 批由又初用插件 S4 测试五步自挂；狂人只管审逻辑、核 Paimon 表结构、prod 发布。

## 坑 / 错误做法

- 仍按 #10785 旧分工等狂人代挂 test 调度 / seed
- ssh 手改测试机 `full_chain.json`，或动 prod 编排
- 控制面硬挪已有组（挪不了）
- S4④/⑤ 选追平水位之后的数据日 → 格子长期 `probe` 等上游，误判为挂失败
- S4⑤ 见「已有补数作业在跑」仍绕开再起（`rerun.py` 同时只许一个）
- 管理报表三表未查上游分区就挂；挂载清单仍带已下线的渠道周/月
- Paimon DDL 未发狂人核就建表

## 正确做法

1. **分工**：test 挂调度、seed → 又初走插件 **S4 五步**（推代码→建表→挂调度→跑一步→定起点补数）；狂人 = 审逻辑 / 核 Paimon 结构 / **prod 发布**。
2. **编排红线**：不许 ssh 手改测试机 `full_chain.json`，不许动 prod 编排；挂调度只走 **S4 ③**。要换组 → S4③ **新建单任务组**，或找狂人。
3. **挂载清单**：渠道周/月先拿掉；管理报表只挂三表（部门周/月 + 产品周）。
4. **追平水位（2026-10-27 口径，预计约 10-30 追平）**：`dim_user_snap` 停 10-22；日间表停 10-24 凌晨；日批线尚未到 10-23 以后。
   - S4④「跑一步」选 **≤10-22** 且上游齐的数据日
   - S4⑤ 补数起点也 **≤10-22**；更晚格子 `probe` 等上游属正常，不算挂失败
5. **管理报表三表上游**：挂前先查 test 最新分区：`ads_channel_metrics_daily_d`、`dim_channel_info_all_snap`；缺则一起挂或先补。
6. **补数互斥**：S4⑤ 提示已有补数作业在跑 → **等完**，勿绕开。
7. **建表**：清单内 Paimon DDL 建表前发狂人核（列/类型/主键/分桶/merge-engine）；SR 影子表找运维建。

## 验证

- S4 ③ 在插件完成，无 ssh 改 `full_chain`
- ④/⑤ 数据日 ≤ 当时追平水位；probe 等待不当失败
- 三表挂前上游 `MAX(dt)` 已核对

## 关联

- bus#11620 / #11621；旧分工 #10785 作废（test 侧）
- lesson：`2026-09-10-pipeline-runner-test四步与test_sandbox铁律.md`、`2026-10-22-mgmt-report-keep-three-tables.md`
- 更新水位后以狂人最新 bus 为准，不必死盯 10-22
