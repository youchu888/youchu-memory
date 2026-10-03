---
date: 2026-10-03
tags: [flink, starrocks, test, ownership, disk, agent-bus]
severity: high
domain: ops
---

# 测试 Flink 不归又初；磁盘满时先腾 SR 再谈重启

## 背景

bus#9731（狂人回 #9730）：又初被指向「测试 Flink 重试」。知秋已定 Flink 作业权限与负责人另派，狂人/又初均无操作权。

## 坑 / 错误做法

- 向狂人/又初催 Flink 重启或自行登 Flink 控制台重试
- 告警疑似 SR 磁盘满时仍只重启 Flink（sink 写不进，作业会再挂）

## 正确做法

1. **Flink 运维**：问知秋「测试 Flink 现负责人是谁」，由该人操作；又初/狂人不接 Flink 重启
2. **现象备忘**：测试 Flink 曾于 **2026-10-02 北京时间 20:53** 重启一次，之后照样挂
3. **同源线索**：同时段测试海豚多表失败告警含 `backend 11004 exceed limit usage`（测试 SR 磁盘满嫌疑；狂人未登机核实）
4. **处置顺序**：若磁盘满确认 → **先腾测试 SR 磁盘** → 再由 Flink 负责人重启；光重启无效
5. **又初侧查盘**：`SHOW BACKENDS` 需 SYSTEM `OPERATE`/`NODE`；当前 `dc_admin` Access denied，须平台/知秋侧核实磁盘，勿假装已验

## 验证

- bus 回执写明：未动 Flink、未假查盘、下一步找知秋问负责人 + 磁盘清腾

## 关联

- bus#9731 / #9730
- StarRocks 错误：`exceed limit usage` / BE 11004
