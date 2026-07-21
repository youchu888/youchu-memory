---
name: 血缘起点是 Kafka 消息，不是 dwd
description: 任何血缘分析都必须把数据起点画到 Kafka 事件消息，dw 是统一具化层，dwd 是按事件类型的二次拆分，不能把 dwd 当源头。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
血缘分析的起点 **永远是 Kafka 事件消息**，不是 dwd。

**数据流原则**：

```
Kafka 事件消息（多种事件混在一起）
  ↓ Flink: db/flink-sql/数据分流.sql
dw.dw_user_event_detail  ← 把 Kafka 消息原样具化为统一明细，跨业务、跨事件
  ↓ 按事件类型 / 业务域拆分（离线 ETL）
dwd.dwd_*  ← 每张表代表一类已具化的事件（注册、登录、订单创建、视频播放、广告点击……）
  ↓
dws / ads
```

**Why**：用户多次纠正过——"dwd 不是数据去的起点，数据起点都是 kafka 的消息，但我们会把消息具化为不同的事件"。把 dwd 当起点会丢掉真正的源头信息（消息 topic、Flink 分流逻辑、具化口径），下游想排查脏数据/补数都没法回到根。

**How to apply**：
1. 任何血缘报告/Mermaid 图，最顶部都要画 Kafka 节点（用户行为日志 topic、结算业务消息 topic 等），明确连到 Flink → dw 层
2. dwd 节点不能作为图的根，必须被 `dw.dw_user_event_detail` 喂；如果某 dwd 表是 Flink 直接从 Kafka 写的（不经 dw），单独标注，不要省略 Kafka 起点
3. **每次开始分析必须先重新读本地 sqlite 拿 `release_status`**，`retired` 的表直接整张剔除：
   - 不进表清单
   - 不进 Mermaid 图（不要保留 "🚫 retired" 占位行）
   - 它的上游若仅给它用，也连带剔除（例：`ads.ads_ad_click_user_daily_d` retired → `dwd.dwd_ad_click_d` 不再追溯）
4. 公共维度（dim.*）和外部项目的 dwd 用作上游时，标 `[外部]`，但仍要回溯到它们的 Kafka 起点说明
5. 每次重做分析前都要 `sqlite3 metadata/metadata.db` 重新查表项目归属与状态，**不能依赖上一次的内存或上次的报告**
