---
name: StarRocks DDL DEFAULT 值要慎用
description: StarRocks 不允许 ALTER 修改列默认值；DEFAULT CURRENT_TIMESTAMP 在主键表 UPDATE 时会踩坑
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
给 StarRocks 表加 `DEFAULT` 值（尤其 `DEFAULT CURRENT_TIMESTAMP`）要慎重。

**Why:** 两个已踩过的坑：
1. **DEFAULT 值改不了**：StarRocks 不支持 ALTER 修改列的默认值，想撤回只能 drop + create + 回刷全量。
2. **主键表 UPDATE 会触发 DEFAULT**：StarRocks 主键表的 UPDATE 实质是 delete+insert，未显式 SET 的 `DEFAULT CURRENT_TIMESTAMP` 字段会被刷成当前时刻。dim_user_all 的 `channel_updated_time` 就是因此被 migration Step 3 一次 UPDATE 全部污染成执行时刻，导致 1.51 亿 organic 用户莫名有了 channel_updated_time。

**How to apply:**
- 新建表时默认**不**给字段加 `DEFAULT`（尤其 `DEFAULT CURRENT_TIMESTAMP`），除非：
  - 确定永远不会在 UPDATE 中"遗漏"这个字段
  - 且业务语义上 DEFAULT 值确实是"正确填充"
- 创建时间这类字段，改由 ETL 脚本显式写 `CURRENT_TIMESTAMP()`，给自己保留掌控权
- 审查别人写的 DDL 时，看到 `DEFAULT` 就停下来问一句："UPDATE 这行时漏掉这字段会发生什么？"
- 如果真的发现有 DEFAULT 要去掉，做好"重建表 + 回刷全量"的预算
