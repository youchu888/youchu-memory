---
date: 2026-06-27
tags: [worker_ant, starrocks, etl, datacheck, migration, dolphin, anti-crawler, agent-bus]
severity: high
domain: ops
source: worker_ant agent-bus bus#77 (全量协作知识·核心包)
---

# 工作狂人《全量协作知识·核心包》

> 穷尽版待 worker_ant 清空上下文后补充。本文为核心准确版。

## 1. SR / SQL / ETL 方言 + 模型选型

- UPDATE target **不能起别名**
- **DUPLICATE 模型不支持 UPDATE**
- 主键表 UPDATE = delete + insert；未显式 SET 的 **DEFAULT 字段会被刷成当前值**（慎用 `DEFAULT CURRENT_TIMESTAMP`）
- 跨天 UV / 去重：`bitmap_union` / `bitmap_count`
- `DATETIME BETWEEN` **上界半开**（`<` 次日 0 点）
- 明细 DUPLICATE KEY 选什么 = 去重维度：`KEY=(event_time, app_id)` 则**不去 event_id**，源 event_id 重复原样进表
- 自动分区表（`PARTITION BY date_trunc`）幂等写法：
  - ✅ `SET dynamic_overwrite=true` + `INSERT OVERWRITE`（无分区子句）
  - ❌ `OVERWRITE PARTITION(pX)` → Unknown partition
  - ❌ `INSERT INTO` → 重跑堆重复
- 大表 `count(distinct)` 易爆内存 → scope 到单 app / 单小时

## 2. 核查 / 对账 / 迁移

- 抽样必带 **event_id**；按 **app_id** 独立核算
- **缺数三步法**：源 `dw` → 新源 `_new` → 脏表 `error_value` **值对值坐实**（别从规则猜）
- 判迁移状态：**必拉 live task SQL**（别信快照 / catalog 旧 flag）
- 判幂等：dwd 表 `count` 跟源 `_new` **逐位比**，相等 = 一次 overwrite 非累积
- **cat 分类**：
  - cat1 天表 14 张 / cat2 天+小时 5 / cat3 小时 2 / cat4 小时 / cat5 渠道 dws 3
  - 判据：**没对应 temp 表 + 任务源是 `dw_user_event_detail_new` = 已迁移**

## 3. 海豚 test / prod

| 环境 | DS | 地址 | 接入 |
|------|-----|------|------|
| test | 3.1.9 | 43.212.183.54 | MCP + REST |
| prod | 3.4.1 | 13.212.153.182 | REST；wf 列表用 `workflow-definition` 非 `process-definition` |

- 拉 live task SQL：`GET /projects/{proj}/workflow-definition/{code}` → `taskDefinitionList` → `taskParams.sql`
- 改 task：**必先 OFFLINE wf**；改 task 改全链；`flag=NO` = 废弃跳过

## 4. dw / dwd / dws / ads + 脏表 + 反扒

| 层 | 说明 |
|----|------|
| dw | 源明细；必加 event_time 边界；保留期有限，追历史去 dwd |
| dwd | 清洗明细 |
| dws | 汇总 |
| ads | 应用 |

- **脏表**：`paimon.dw.dwd_standard_dirty_data_df`（prod paimon **dw** 库；`error_column` / `type` / `value` + `raw_data`）
- `_new` = OM 清洗产物；丢的进脏表
- **反扒**：判 bot 禁用空值衍生 groupby；验证必 **prod** 不用 test（稀疏）

## 5. 踩坑案例

### watch_video

- 别凭记忆说 INSERT INTO；**拉 live**（test+prod 现都已 `dynamic_overwrite` 修复）
- 5.78% 重复 = 源 `dw_new`(video_event) **自身 event_id 重复**，非任务累积（prod 表 count 与源逐位相等）

### page_click

- 屏幕点击记**坐标**（x/y + percent + 屏幕尺寸），**非导航**；量大正常
- 判 bot：先立基线（正常 2~4 taps/event_ts）+ 看坐标网格化 + 多信号；别拿量/粗间隔想当然（over-read 3 次）

### product_id

- `order_paid` distinct product_id 降 = 迁移切 `_new`（疑 `isRequired` 清洗副作用）

### 通用

- prod `my.cnf` = **52.221.240.167**（别连 test 43.212.x = 假异常）
- 部署后端 **pkill 后必确认 bind** 再宣布（宕机过）

## 6. dc-platform 必读文档 slug

`GET /api/v1/platform/docs/raw/{slug}` + Bearer token

- `dwd_active_table_catalog`
- `dwd_migration_part1_online_impact`
- `dwd_migration_part2_cat45_double_run`
- `geo_region_standardization_design`
- `user_tagging_design`
- `dw_sdk_field_upgrade_proposal`
- `api-reference`

## 7. agent-bus / 协作礼仪

- bothub 发用 agent 名（`youchu_ai` / `dc_cursor_bot`）；群里用昵称（初儿 / 猫猫 / 花儿）
- 确认消息写 **「不用回」** 避免 bot 互刷
- 派活写明环境（prod my.cnf + host）
- **转述别人的数前自己 prod 复核**（蓝猫连错 test SR 教训）

## 验证

- prod：`mysql --defaults-file=.claude/database/my.cnf.prod`
- live SQL：海豚 REST `workflow-definition/{code}`
- 脏表：`SELECT * FROM paimon.dw.dwd_standard_dirty_data_df WHERE ... LIMIT`

## 关联

- 速查 v1：`20260626-worker-ant-collab-cheatsheet.md`
- 索引：`~/.dc-platform/memory/worker_ant/INDEX.md`
