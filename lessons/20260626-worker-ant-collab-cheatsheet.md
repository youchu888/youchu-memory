---
date: 2026-06-26
tags: [worker_ant, starrocks, datacheck, prod, migration, agent-bus, dolphin]
severity: high
domain: ops
source: worker_ant via agent-bus bus#72
---

# 工作狂人《数据开发协作速查 v1》+ 近期硬核踩坑

## 背景

工作狂人（worker_ant）经 agent-bus 同步协作知识库，供又初在 prod 核查、迁移对账、海豚运维时复用。

## 《数据开发协作速查 v1》

### StarRocks 方言

- UPDATE target **不能起别名**
- **DUPLICATE 模型不支持 UPDATE**；改值用 INSERT OVERWRITE
- 跨天/跨地区 UV 去重：`bitmap_union` 存、`bitmap_count` 算；可加指标用 SUM
- `DATETIME BETWEEN` **上界半开**（`<` 次日 0 点），否则多算边界

### 核查铁律

1. **抽样必带 event_id**
2. **按 app_id 独立核算**，别混算
3. **缺数三步法**：
   - 先源表（`dw`）vs 产物（`dwd`）对比
   - 再查脏表 `paimon.dw.dwd_standard_dirty_data_df` 的 `error_column` / `error_value`
   - **值对值坐实砍因**，别从规则猜

### 明细查询

- `dw` 明细必加 `event_time` 边界
- 追历史去 **dwd 同期**

### 工具

| 场景 | 工具 |
|------|------|
| 海豚 test | MCP |
| 海豚 prod | REST |
| TG 通知 | `send_tg.py` |
| Agent 互通 | `agent_bus_send.py` |

## 近期硬核踩坑（知秋骂出来的）

| # | 级别 | 规则 |
|---|------|------|
| 5 | 🔴 | **核 prod 必用 prod my.cnf**（`52.221.240.167`），别连 test（`43.212.x`）——数据稀疏满屏假异常（蓝猫翻过车） |
| 6 | 🔴 | **判迁移状态/任务行为必拉 live task SQL**，别信快照/旧记忆 |
| 7 | 🔴 | **判表/字段作用先抽样看真实记录**再下结论；别拿「量大」当异常（page_click = 屏幕点击记坐标，非导航） |
| 8 | | **判幂等**：dwd 表 `count` 跟源 `dw_new count` 逐位比，相等 = 一次 overwrite 非累积；明细 DUPLICATE KEY 不去 event_id，源重复原样进表 |
| 9 | | **改 prod 后端必 pkill 后确认 bind 再宣布** |

## 验证

- prod 连接：`mysql --defaults-file=.claude/database/my.cnf.prod` → host `52.221.240.167:9030`
- dc-platform 文档：`GET /api/v1/platform/docs` + `GET /api/v1/platform/docs/raw/{slug}`（Bearer dcp token）

## 关联

- agent-bus 对接：`omdb/tgbot/docs/AGENT互通对接指南.md`
- 脏数据表：`paimon.dw.dwd_standard_dirty_data_df`
- 来源：worker_ant bus入#14 bus=72
