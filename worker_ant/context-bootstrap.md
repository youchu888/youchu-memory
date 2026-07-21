# 工作狂人 · Agent 上下文注入包

> 又初开工前若任务涉及 **prod 核查 / dwd 迁移 / 对账 / 海豚 / 反扒**，先读此文件 + `INDEX.md` + `lessons/20260627-worker-ant-full-collab-core.md`。

## P0 硬规则（违反会翻车）

1. **prod 必连** `my.cnf.prod` → `52.221.240.167:9030`；test `43.212.x` 稀疏满屏假异常
2. **抽样带 event_id**；按 **app_id** 独立算；**转述别人数据前自己 prod 复核**
3. **判表/字段先抽样真实记录**（page_click=屏幕坐标 x/y，非导航；量大正常）
4. **迁移/任务必拉 live task SQL**（`workflow-definition/{code}`），不信快照/catalog 旧 flag
5. **废弃 _d 表** → 以 `_h`/`_v2` 为准；已迁移判据=无 temp 表 + 源 `dw_user_event_detail_new`
6. dw 明细必 `event_time` 边界；缺数三步：dw → _new → 脏表 `paimon.dw.dwd_standard_dirty_data_df` 值对值
7. 自动分区幂等：`SET dynamic_overwrite=true` + `INSERT OVERWRITE`；❌ PARTITION(pX) / ❌ INSERT INTO 重跑

## P1 ETL / 模型

- UPDATE 不起别名；DUPLICATE 不支持 UPDATE；PK UPDATE 会刷未 SET 的 DEFAULT
- DUPLICATE KEY 维度决定去不去 event_id（KEY 不含 event_id 则源重复原样进）
- 大表 count(distinct) scope 到单 app/单小时

## P1 海豚

- test DS3.1.9 `43.212.183.54`（MCP+REST）；prod DS3.4.1 `13.212.153.182`（REST，`workflow-definition`）
- 改 task：先 OFFLINE wf；flag=NO 废弃跳过

## P1 活跃表 + 迁移

- 25 表见 `dwd_active_table_catalog`；cat1~5 分类见全量 core lesson
- watch_video 5.78% 重复=**源 dw_new 自身重复**，非任务累积（count 逐位比源）

## P2 协作

- bothub 用 agent 名；确认写「不用回」防互刷；派活写明 prod host
- **agent-bus poller**：offset 落 `.cursor/agent-bus/{agent}.offset`；逐条推进；首轮跳 backlog；「待命中/挂起/不用回」不自动发「开始核查」

## P3 反扒对标（2026-06-27 知秋挂起）

- 活跃 PV 反扒 device 层仅挖 0.38%，大头在 NAT/哨兵/匿名；**挂起**等 SDK 新上报后再优化
- 又初已撤待命，不复核不等派

## 完整索引

`~/.dc-platform/memory/worker_ant/INDEX.md`

## 每日学习

每天 **19:30** → `sessions/YYYY-MM-DD.md`

## 进化日志 · 2026-06-27

- bus#101：poller offset 四步修法已落 lesson + 改 `agent_bus_watcher.py`/`agent_bus_client.py`
- bus#102：记忆体系方法论（三级分层/Why+How/触发词）已落 lesson + 更新 MEMORY/_index
- 派单礼仪：「待命中/挂起/不用回」→ learn_only 或短回执，禁止重复「开始核查」
- 反扒 PV 交叉复核三项一致已结案；对标专项知秋挂起，又初已撤
