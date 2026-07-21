---
name: 数据违规必须给原始明细行
description: 报告数据质量违规时必须给出表里能直接定位的真实行（event_id/PK/时间等），不能只给统计或意译描述。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
汇报数据质量违规 / 数据核查异常 / 数据样本时，**必须直接给数据库里能 SQL 定位的真实行**：
- 主键 / 业务 ID（如 `event_id`、`order_id`、`uid`、`device_id`）
- 时间字段（`event_time` 精确到秒）
- 关键内容字段的**完整原值**（不要省略号、不要意译、不要做归类摘要）
- 必须可以直接拼成 `WHERE pk IN (...)` 把这些行从生产库找回来

**Why**：用户要根据这些违规行去库里追查、修复、向上游索赔。**给统计数（"18 行违规"）+ 归类摘要（"6 类剪贴板内容"）没有说服力**，用户没法据此回到库里定位证据。

**How to apply**：
1. 跑核查 SQL 时，违规分支永远 `SELECT event_id, event_time, app_id, uid, device_id, ...完整字段` 而不是 `SELECT COUNT(*)`
2. 输出明细表必须包含 `event_id` / `dt` / `event_time` 等可索引字段，且字段值**不截断**
3. 报告末尾附"复现 SQL"——`SELECT * FROM tbl WHERE event_id IN (...)`，让用户一键拉回原始行
4. 异常长字段（如剪贴板 trace_id）也必须**完整显示**，不能用"等"、"…"、"前 100 字符"代替——这是判定 ETL 是否该丢弃的关键证据
