---
name: SQL DATETIME 列 BETWEEN 字符串上界的边界 bug
description: 字符串日期 'YYYY-MM-DD' 在和 DATETIME 列比较时被 cast 成 'YYYY-MM-DD 00:00:00'，BETWEEN 上界写日期会漏掉当天 00:00:00 之后的所有数据。
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
写 ETL 时，**DATETIME 列**和**字符串日期**做 BETWEEN 比较，**上界要小心**：

```sql
-- ❌ 错（漏掉当天 00:00:01 之后所有数据）
WHERE dt_time BETWEEN '$[yyyy-MM-dd-31]' AND '$[yyyy-MM-dd-1]'
                                                 ↑
                              cast 成 'YYYY-MM-DD 00:00:00' (凌晨 0 点)

-- ✅ 对（半开区间到 T 日 0 点）
WHERE dt_time >= '$[yyyy-MM-dd-31]'
  AND dt_time <  '$[yyyy-MM-dd]'      -- T 日 0 点（不含），覆盖 T-1 整天

-- ✅ 对（也行，但必须显式写时分秒）
WHERE dt_time BETWEEN '$[yyyy-MM-dd-31] 00:00:00' AND '$[yyyy-MM-dd-1] 23:59:59'

-- ✅ 对（用 DATE() 转换，但破坏索引）
WHERE DATE(dt_time) BETWEEN '$[yyyy-MM-dd-31]' AND '$[yyyy-MM-dd-1]'
```

**Why**：StarRocks（其他 SQL 引擎多数也一样）拿字符串和 DATETIME 比较时会 cast 字符串到 DATETIME。`'2026-05-01'` cast 成 `'2026-05-01 00:00:00'`。`<= '2026-05-01'` 等价于 `<= '2026-05-01 00:00:00'`，**T-1 当天 00:00:01+ 的所有数据都被排除**。

**How to apply**：

1. **DATETIME 列**用半开区间 `>= start AND < end_exclusive`，end_exclusive 用 T 日 0 点（即 `$[yyyy-MM-dd]`）
2. **DATE 列**和字符串日期 BETWEEN 没问题（两边都是 DATE 类型，日界对齐），不需要改
3. 看到 `BETWEEN '$[yyyy-MM-dd-X]' AND '$[yyyy-MM-dd-Y]'` 这种 pattern 立刻警觉，看左边列是不是 DATETIME

**典型实例**（2026-05-02 实际修过的）：
- [dws_user_first_recharge_retention_d.sql](../../../Program/datacenter/dc-parent/ops_system/04.dws/dws_user_first_recharge_retention_d/dws_user_first_recharge_retention_d.sql) 第 38 行 `where dua.first_recharge_time between '$[yyyy-MM-dd-31]' and '$[yyyy-MM-dd-1]'`
  - first_recharge_time 是 DATETIME
  - 5-2 跑时 `between '2026-04-01' and '2026-05-01'` 漏掉 5-1 当天 25450 个首充用户
  - 修法：改成 `>= '$[...-31]' and < '$[yyyy-MM-dd]'`

**症状识别**：
- 任务跑了（update_time / partition VisibleTime 显示今天有写入）
- 但 max(dt) 比预期少 1 天
- 上游表里实际有 T-1 当天数据
- 用任务原 WHERE 重跑 SELECT 也确认 T-1 没数据
- → 90% 概率是这个 bug

**自动扫描**：
```bash
grep -rEn "BETWEEN\s+'[^']*\\\$\\[yyyy" ops_system  # 找出所有 BETWEEN $[yyyy-...] 写法
# 然后人工核对每处的左边列是不是 DATETIME
```
