# 渠道评分表条件查询规则

表：`dws.dws_user_promotion_behavior_d`

## 标准参数映射
- `startTime` / `endTime` → 指标时间范围（具体映射看指标定义）
- `activityStartTime` / `activityEndTime` → `dt`（结算日/活动日）范围
- `channelCode` → `channel`
- `appId` → `app_id`

## 指标定义

### 注册人数
- 含义：注册用户去重计数
- 时间字段：`register_date`，使用 `startTime ~ endTime` 对应的日期部分
- 公式：`COUNT(DISTINCT uid)`
- 条件：`register_date >= startDate AND register_date <= endDate`

### 金额类指标（统一规则）
- 时间条件与注册人数完全一致：`register_date` 在 `startTime~endTime`，`dt` 在 `activityStartTime~activityEndTime`
- 具体指标：
  - 充值金额：`ROUND(SUM(recharge_amount), 2)`
  - VIP充值金额：`ROUND(SUM(vip_charge_amount), 2)`
  - 扣费VIP充值金额：`ROUND(SUM(deduction_vip_charge_amount), 2)`
  - 金币充值金额：`ROUND(SUM(coin_charge_amount), 2)`
  - 消费金额：`ROUND(SUM(consume_amount), 2)`

## 查询模板
```sql
SELECT <指标>
FROM dws.dws_user_promotion_behavior_d
WHERE channel = '{channelCode}'
  AND app_id = '{appId}'
  AND register_date >= '{startDate}'
  AND register_date <= '{endDate}'
  AND dt >= '{activityStartDate}'
  AND dt <= '{activityEndDate}';
```

注意：startDate/endDate 从 startTime/endTime 取日期部分即可。
