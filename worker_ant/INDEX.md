# 工作狂人知识库 · 总索引

> 最后更新：2026-06-27 · 又初维护

## 快速检索

| 我想… | 去哪 |
|--------|------|
| **全量协作核心** | [全量核心包](../lessons/20260627-worker-ant-full-collab-core.md) |
| 协作硬规则 / 踩坑简版 | [协作速查 v1](../lessons/20260626-worker-ant-collab-cheatsheet.md) |
| 每日学习流程 | [README](./README.md) · [DAILY_PROMPT](./DAILY_PROMPT.md) |
| 某日问答原文 | `sessions/YYYY-MM-DD.md` |
| dwd 25 表清单 | dc-platform `dwd_active_table_catalog` |
| 迁移对账 Part1/2 | `dwd_migration_part1_online_impact` / `part2` |
| Agent 冷启动摘要 | [context-bootstrap.md](./context-bootstrap.md) |

---

## A. 又初 lesson（canonical）

| 日期 | 文件 | tags | 一句话 |
|------|------|------|--------|
| 2026-06-27 | [全量核心包](../lessons/20260627-worker-ant-full-collab-core.md) | worker_ant, etl, migration | SR幂等/cat/海豚API/踩坑/文档slug；bus#77 |
| 2026-06-27 | [offset 四步修法](../lessons/20260627-agent-bus-offset-persistence.md) | agent-bus, poller | after_id 落盘/防 backlog 重放；bus#101 |
| 2026-06-27 | [记忆体系方法论](../lessons/20260627-worker-ant-memory-architecture.md) | memory, self-evolve | 三级分层/触发词/Why+How；bus#102 |
| 2026-06-26 | [协作速查 v1](../lessons/20260626-worker-ant-collab-cheatsheet.md) | worker_ant, prod, datacheck | 简版速查；bus#72 |

---

## B. dc-platform 文档（worker_ant 推荐必读）

> API：`GET /api/v1/platform/docs` · 正文：`GET /api/v1/platform/docs/raw/{slug}` + Bearer token

### 迁移 / dwd

| slug | 标题 | 优先级 |
|------|------|--------|
| `dwd_active_table_catalog` | dwd 主表迁移方案 · 25 表 5 分类 | P0 |
| `dwd_migration_part1_online_impact` | Part1 已上线 cat1/2/3 + 下游 | P0 |
| `dwd_migration_part2_cat45_double_run` | Part2 cat4/cat5 双跑对账 | P0 |
| `dw_sdk_field_upgrade_proposal` | 反爬·影子表·双引擎 | P1 |

### 反爬 / 方法论

| slug | 标题 | 优先级 |
|------|------|--------|
| `methodology` | 反扒方法论 · 维度可信度 | P0 |
| `storage_strategy` | 入库前杀 vs 入库后过滤 | P1 |
| `rules_pattern_a_aws_farm` | Pattern A AWS 农场 | P2 |
| `rules_pattern_b_cn_scan` | Pattern B CN 扫描 | P2 |
| `sdk_field_anti_crawler_review` | SDK 字段 review v4.8 | P1 |
| `device_fingerprint_analysis` | device_fingerprint 分析 | P2 |

### 标签 / 地区 / 其他

| slug | 标题 | 优先级 |
|------|------|--------|
| `user_tagging_design` | 用户标签体系设计 | P1 |
| `geo_region_standardization_design` | 地区标准化 GeoNames | P2 |
| `dynamic_tracking_pool_design` | 动态跟踪池表设计 | P2 |
| `industry_benchmark_and_roadmap` | 业界对比 + 路线图 | P3 |
| `api-reference` | API 参考 | P2 |

---

## C. 主题速查（来自工作狂人 + 当日实践）

### StarRocks 方言

- UPDATE target 不起别名；DUPLICATE 不支持 UPDATE → INSERT OVERWRITE
- UV：`bitmap_union` / `bitmap_count`；`bitmap_hash64_udf` 是 global
- `DATETIME BETWEEN` 上界半开 `<` 次日 0 点

### 核查铁律

1. 抽样必带 `event_id`
2. 按 `app_id` 独立核算
3. 缺数：dw vs dwd → `paimon.dw.dwd_standard_dirty_data_df`（error_column/error_value 值对值）
4. dw 明细必 `event_time` 边界；追历史去 dwd 同期

### prod / test

- 🔴 核数 **prod** `52.221.240.167`（`my.cnf.prod`）
- test `43.212.x` 稀疏 → 假异常（蓝猫翻车）

### 迁移 / 表状态

- **活跃 25 表**：见 `dwd_active_table_catalog`（只核这 25）
- **废弃勿报**：`coin_consume_d`/`order_created_d`/`ad_click_d` 等 → 以 `_h`/`_v2` 现表为准
- cat5：temp(_new) vs 正式(老 dw)；行差 1~9%，recharge 几乎平
- Part1 结论：新源非老源超集，系统性轻中度少算在源头；无灾难塌方

### 海豚 / 工具

- test DS3.1.9 `43.212.183.54`（MCP+REST）；prod DS3.4.1 `13.212.153.182`（REST，`workflow-definition`）
- 拉 live SQL：`GET .../workflow-definition/{code}` → `taskParams.sql`；改 task 先 OFFLINE wf
- 通知：`send_tg.py`；互通：`agent_bus_send.py`
- 自动分区幂等：`SET dynamic_overwrite=true` + `INSERT OVERWRITE`（无分区子句）

### 迁移 cat 分类

- cat1 天14 / cat2 天+小时5 / cat3 小时2 / cat4 小时 / cat5 dws3
- 已迁移判据：无 temp 表 + 源 `dw_user_event_detail_new`

### 已知真问题（截至 2026-06-26）

| 表/主题 | 现象 | 状态 |
|---------|------|------|
| `dwd_user_watch_video` | event_id 日重复 5.78% | **源 dw_new 自身重复**，非任务累积（count 逐位比源） |
| `dwd_order_created_h` | 连涨 5 天 | 增长趋势，非 bug |
| `dwd_order_paid_d` product_id | distinct 骤降 ~30% @ cat1 切 _new | 真信号，保留 |
| `dwd_keyword_search_d` | event_id 重复 1.7% | 待关注 |

---

## D. 学习会话流水

| 日期 | 文件 | 摘要 |
|------|------|------|
| 2026-06-27 | [sessions/2026-06-27.md](./sessions/2026-06-27.md) | 全量核心包+进化完成；反扒挂起撤 |
| 2026-06-26 | [sessions/2026-06-26.md](./sessions/2026-06-26.md) | 速查v1入库；25表+cat5核对；全量学习请求 bus#76 |

---

## E. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-06-27 | 全量核心包 lesson + context-bootstrap 升级 | bus#77 |
| 2026-06-26 | 初建知识库；INDEX + 每日学习机制；协作速查 v1 入库 |
