# 确认稿 · 注册人数业务日归属（A + 截止线）

> 状态：**方向已定，尚未正式开工改代码**（知秋：不急，归因先跑完）  
> 来源：知秋 2026-09-09 原则 + 狂人 bus#8332 落成  
> 禁止：再推产品 A/B 二选一；禁止用 `now()` / 跑批时刻当截止线

## 定案（一个方案，不是裸 A）

注册人数按 **event_time 所在自然日** 归业务日，并加 **request_time 绝对截止线**；晚于截止线的明确放弃、不追。

三件事缺一不可：

| # | 规则 | 说明 |
|---|------|------|
| 1 | **归属键 = `event_time`** | 与 `dwd.dwd_user_register_d_v2` 一致；业务日 = `DATE(event_time)` |
| 2 | **读两天分区 `dt` 与 `dt+1`** | 业务日晚上的注册常落在次日分区；只读当天分区会漏 |
| 3 | **截止线 = 从业务日推出的绝对时刻** | `request_time < (业务日 + 1 天 + 3 小时)`；例：业务日 09-03 → 截止 `2026-09-04 03:00:00` |

## 截止线（写错则前功尽弃）

```text
cutoff = TIMESTAMP(业务日 dt) + 1 day + 3 hours
纳入条件：request_time < cutoff
```

伪 SQL（示意，开工后再落 ETL）：

```sql
-- 业务日 :biz_dt
SELECT ...
FROM dwd.dwd_user_register_d_v2
WHERE dt IN (:biz_dt, DATE_ADD(:biz_dt, INTERVAL 1 DAY))   -- 两天分区
  AND DATE(event_time) = :biz_dt                            -- 归属
  AND request_time < DATE_ADD(CAST(:biz_dt AS DATETIME), INTERVAL 27 HOUR)
  -- 27h = 次日 03:00；等价于 request_time < TIMESTAMP(:biz_dt + 1 day || ' 03:00:00')
```

**禁止**：`request_time < NOW()` / `CURRENT_TIMESTAMP()` / 调度触发时刻——同一天重跑结果会变，不可复现。

调度约束（原则侧）：此类任务放在 **03:00 之后槽位**，与「等到 3 点」一致；口径本身仍用绝对时刻，不绑跑批墙钟。

## 与 8,189 / 8,191 差额的关系

YC-001 那批：SR 落 09-03、`event_time` 集中在 22–23 点，是 **切天边界不同**，不是缺数。

按本口径：

- 归 **3 号**（`event_time` 所在日）
- 若 `request_time` 在 `09-04 03:00` 之前 → **纳入 3 号**
- **不再算进 4 号**

## 开工门禁

- 本文仅确认稿；**知秋正式说开始再改代码 / 发海豚**
- 归因当前优先；本口径变更排队

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-09-09 | 按 bus#8332 从「A/B 二选一」改为单一「A + request_time 截止线」 |
