---
date: 2026-06-17
tags: [starrocks, ddl, alter, primary-key, default]
severity: high
domain: sql
---

# StarRocks ALTER：DEFAULT 裸数字 + 主键列禁止 MODIFY

## 背景

生产执行归因相关 DDL 四条，②④ 因 StarRocks 语法/模型限制失败。

## 坑 / 错误做法

1. `ADD COLUMN ... TINYINT DEFAULT 0` → `Unexpected input '0'`（期望 NULL / CURRENT_TIMESTAMP / **带引号字符串**）
2. ① 失败后仍跑 UPDATE → `column does not exist`（连带失败，非独立问题）
3. `MODIFY COLUMN uid` on `dws_register_attribution_result_d` → `Can not modify key column: uid`（PRIMARY KEY 表 key 列不可 MODIFY）

## 正确做法

### ①② dim 加 is_rewrite_channel

```sql
ALTER TABLE dim.dim_app_attribution_config
ADD COLUMN is_rewrite_channel TINYINT NULL
COMMENT '是否回写 dim_user_all.channel：1=启用，0=仅计算落结果表';

UPDATE dim.dim_app_attribution_config
SET is_rewrite_channel = 0,
    update_time = CURRENT_TIMESTAMP()
WHERE is_rewrite_channel IS NULL;
```

若坚持 DEFAULT：部分版本可试 `DEFAULT "0"`，但项目惯例**不加 DEFAULT**（UPDATE 主键表会触发默认值副作用）。

### ③ dwd attribution_flag

已成功，无需重跑。

### ④ dws uid 扩 varchar(128)

`PRIMARY KEY(dt, app_id, uid, register_event_id)` 中 **uid 是 key 列**，只能：

- **方案 A**：uid 实际 ≤64 → 保持 varchar(64)，跳过
- **方案 B**：必须 128 → 建新表（uid varchar(128)）→ INSERT SELECT → 换名 / 回刷分区

不能 `ALTER ... MODIFY` key 列。

## 验证

```sql
DESC dim.dim_app_attribution_config;          -- 应有 is_rewrite_channel
SELECT is_rewrite_channel, COUNT(*) FROM dim.dim_app_attribution_config GROUP BY 1;
DESC dwd.dwd_user_register_d_v2;            -- 应有 attribution_flag
SHOW CREATE TABLE dws.dws_register_attribution_result_d;  -- uid 仍为 varchar(64) 除非走方案 B
```

## 关联

- 脚本：`ops_system/04.dws/dws.dws_register_attribution_result_d/dim_app_attribution_config_add_is_rewrite_channel.sql`
- feedback：`feedback_starrocks_default_value_caution.md`
