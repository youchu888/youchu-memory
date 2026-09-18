# dws.dws_user_promotion_behavior_h 数据核查剧本

## 1. 表信息
- 表名：`dws.dws_user_promotion_behavior_h`
- 业务别名：**渠道评分表（小时）**
- 状态：上线
- 粒度：`hour + dt + channel + app_id + uid`（DUPLICATE KEY；`device` 不在键里，同 uid 跨 device 可多行）
- 绑定程序：`/ops_system/04.dws/dws_user_promotion_behavior_h/dws_user_promotion_behavior_h.sql`

## 2. 与主剧本的关系

**核查规则一律复用** [dws.dws_user_promotion_behavior_d.md](dws.dws_user_promotion_behavior_d.md)。

小时表特有注意点：
- **`is_*` tinyint 标志**跨小时逐行 =1，`SUM(is_*)` 会膨胀。必须先按 `(dt,channel,app_id,uid)` 做 `MAX(is_*)` 去重再 SUM，见主剧本 part_01。
- **小时核对默认覆盖昨天 + 今天**（`dt IN (T-1, T)`），今天取已到达的小时分区。
- 金额字段精度为 `decimal(18,2)`（注意 behavior_d 用 `decimal(18,4)`）；比较用 `ROUND(x, 2)`。

## 3. 核查入口

- `/datacheck dws.dws_user_promotion_behavior_h` → 直接执行主剧本 part_01~part_03，过滤条件 `channel IS NOT NULL AND channel != 'organic'`。
- 若只需小时切片与 charge_h 的对比，只跑主剧本 part_02 的小时段。

## 4. 报告落地
- 默认路径：`.claude/database/reports/dws.dws_user_promotion_behavior_h/`
- 或与主表复用同一目录：`.claude/database/reports/dws.dws_user_promotion_behavior_d/`（当同批次四表一起核查时）
