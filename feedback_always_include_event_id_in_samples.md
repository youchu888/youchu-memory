---
name: 样本数据必须包含 event_id
description: 所有抽样明细数据都要带上 event_id 字段
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
所有样本明细数据都要包含 `event_id`。

**Why:** 用户明确要求"以后所有样本都要给 event_id"。event_id 是事件唯一标识，方便定位和追溯原始数据。

**How to apply:** 查数据抽样时，SELECT 列表里必须包含 event_id（通常放在 app_id、uid 之后）。
