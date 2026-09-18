# 测试库 LTV / 首充留存 数据比对报告

- **环境**：测试 StarRocks（`my.cnf.test`）
- **比对时间**：2026-05-25
- **新链路**：`dws_user_reg_ltv_d_h`、`dws_user_first_recharge_retention_d_h`
- **旧链路**：`dws_user_reg_ltv_daily_d`、`dws_user_first_recharge_retention_d`（物理表，兼容 VIEW 未建）
- **结论**：SQL 不改；差异来自 cohort / 活跃口径升级，日汇总层面可接受

---

## 1. 覆盖范围

| 表 | min_dt | max_dt | 分区天数 | 核心指标合计 |
|----|--------|--------|----------|--------------|
| `dws_user_reg_ltv_d_h` | 2026-03-01 | 2026-05-25 | 86 | new_users **1,184,133** |
| `dws_user_reg_ltv_daily_d`（旧） | 2026-01-20 | 2026-05-24 | 93 | new_users **1,178,133** |
| `dws_user_first_recharge_retention_d_h` | 2026-02-24 | 2026-05-24 | 82 | first_recharge **16,499** |
| `dws_user_first_recharge_retention_d`（旧） | 2026-03-09 | 2026-05-24 | 74 | first_recharge **16,482** |

**说明**

- 2026-01~02 无 `_h` 数据：`dim.dim_user_all` 在测试环境该段几乎无注册 cohort（非补数失败）。
- 首充 `_h` 比旧表多覆盖 **2026-02-24 ~ 03-08**（旧表从 03-09 才有分区）。
- 首充旧表合计 16,482 vs `_h` 16,499：旧表缺早期 17 人 + 与 dim 全量 16,499 对齐。
- LTV `_h` 多 **05-25** 一日（T+0 小时/日批已写入）。

---

## 2. LTV：`new_users` 日汇总对比

### 2.1 2026-05-06 ~ 05-24（主验证窗，dim 注册量充足）

| dt | _h new_users | 旧表 new_users | diff |
|----|-------------|----------------|------|
| 2026-05-06 | 13,421 | 13,422 | -1 |
| 2026-05-07 | 12,388 | 12,391 | -3 |
| 2026-05-08 | 14,449 | 14,449 | 0 |
| 2026-05-09 | 18,279 | 18,280 | -1 |
| 2026-05-10 | 21,566 | 21,566 | 0 |
| 2026-05-11 | 17,137 | 17,137 | 0 |
| 2026-05-12 | 20,268 | 20,268 | 0 |
| 2026-05-13 | 20,527 | 20,527 | 0 |
| 2026-05-14 | 19,286 | 19,288 | -2 |
| 2026-05-15 | 21,211 | 21,215 | -4 |
| 2026-05-16 | 23,433 | 23,433 | 0 |
| 2026-05-17 | 23,920 | 23,921 | -1 |
| 2026-05-18 | 18,302 | 18,309 | -7 |
| 2026-05-19 | 16,457 | 16,457 | 0 |
| 2026-05-20 | 15,282 | 15,282 | 0 |
| 2026-05-21 | 14,686 | 14,686 | 0 |
| 2026-05-22 | 16,319 | 16,319 | 0 |
| 2026-05-23 | 19,615 | 19,615 | 0 |
| 2026-05-24 | 17,857 | 17,857 | 0 |

**汇总**：19 天中 12 天完全一致；有差异 7 天，最大 diff **-7 人**（05-18）。

### 2.2 2026-03-01 ~ 05-05（早期重叠段）

- 03-01 ~ 03-12：diff 较大（**-127 ~ -234 人/日**），旧表系统性偏高。
- 03-13 起：diff 收敛至 **-1 ~ -6 人/日**（与 5 月主验证窗一致）。
- **根因**：旧表 cohort 来自 `dwd_user_register_d_v2` + 事件去重；新表来自 `dim.dim_user_all.register_time`，早期测试数据两源不一致。

### 2.3 维度粒度 diff

```sql
-- 05-06~05-24，五维 join 后 new_users 不一致行数
SELECT COUNT(*) FROM ... WHERE BITMAP_COUNT(h.new_users) <> o.new_users;
-- 结果：21,027 行
```

日汇总几乎对齐，但 channel/region/device 拆行有 redistribution（**合计不变或差个位数**），属维度映射差异，非总量丢失。

---

## 3. LTV：`day_0_pay_amount` 日汇总对比（_h 元，旧表分÷100）

| dt | _h (元) | 旧表 (元) | diff (元) |
|----|---------|-----------|-----------|
| 2026-05-06 | 14,430 | 14,330 | +100 |
| 2026-05-07 | 13,909 | 13,689 | +220 |
| 2026-05-08 | 14,580 | 14,535 | +45 |
| 2026-05-09 | 11,889 | 10,958 | +931 |
| 2026-05-10 | 13,760 | 13,760 | 0 |
| 2026-05-11 | 12,544 | 11,849 | +695 |
| 2026-05-12 | 11,580 | 11,480 | +100 |
| 2026-05-13 | 13,265 | 13,220 | +45 |
| 2026-05-14 | 14,200 | 14,200 | 0 |
| 2026-05-15 | 9,829.9 | 9,829.9 | 0 |
| 2026-05-16 | 11,520 | 11,520 | 0 |
| 2026-05-17 | 10,050 | 10,050 | 0 |
| 2026-05-18 | 10,170 | 10,170 | 0 |
| 2026-05-19 | 8,592 | 8,592 | 0 |
| 2026-05-20 | 9,235 | 9,235 | 0 |
| 2026-05-21 | 6,100 | 6,100 | 0 |
| 2026-05-22 | 10,624 | 10,574 | +50 |
| 2026-05-23 | 12,206 | 12,206 | 0 |
| 2026-05-24 | 7,920 | 7,920 | 0 |

**汇总**：19 天中 11 天完全一致；有 diff 8 天，最大 **+931 元**（05-09）。05-15 之后连续 10 天（至 05-24）除 05-22 外全部一致。

---

## 4. 首充留存对比

### 4.1 `first_recharge_users`（cohort 人数）

| 区间 | 结论 |
|------|------|
| 2026-05-06 ~ 05-24 | **_h 与旧表逐日完全一致** |
| 2026-02-24 ~ 03-08 | **_h 有数据，旧表无分区**（旧表 min_dt=03-09） |
| dim 全量 | `dim.dim_user_all` 首充合计 **16,499**，与 `_h` 一致 |

### 4.2 `day1_ret_cnt`（次日留存）

| dt | _h day1 | 旧表 day1 | diff | 备注 |
|----|---------|-----------|------|------|
| 2026-05-06 | 114 | 104 | +10 | |
| 2026-05-07 | 101 | 92 | +9 | |
| 2026-05-08 | 121 | 112 | +9 | |
| 2026-05-09 | 106 | 103 | +3 | |
| 2026-05-10 | 122 | 112 | +10 | |
| 2026-05-11 | 107 | 94 | +13 | |
| 2026-05-12 | 101 | 91 | +10 | |
| 2026-05-13 | 109 | 97 | +12 | |
| 2026-05-14 | 109 | 99 | +10 | |
| 2026-05-15 | 88 | 76 | +12 | |
| 2026-05-16 | 109 | 100 | +9 | |
| 2026-05-17 | 93 | 84 | +9 | |
| 2026-05-18 | 81 | 73 | +8 | |
| 2026-05-19 | 84 | 80 | +4 | |
| 2026-05-20 | 72 | 66 | +6 | |
| 2026-05-21 | 77 | 70 | +7 | |
| 2026-05-22 | 73 | 70 | +3 | |
| 2026-05-23 | 85 | 84 | +1 | |
| 2026-05-24 | 47 | NULL | +47 | 旧表未成熟写 NULL；_h 存 bitmap，VIEW 层 CASE WHEN |

**规律**：成熟日 `_h` day1 **系统性高于旧表 +1~+13**；cohort 人数一致，差异纯来自活跃定义。

| 口径 | 活跃来源 | 关联键 |
|------|----------|--------|
| 旧表 | `dwd.dwd_app_page_view_d` | app_id + uid |
| 新 `_h` | `dws.dws_app_user_d_h.active_users` | app_code + channel（strict-channel） |

### 4.3 异常检查

```sql
-- fr=0 且 day1>0 的行：0 条
SELECT dt, SUM(BITMAP_COUNT(first_recharge_users)) fr, SUM(BITMAP_COUNT(day1_ret_cnt)) d1
FROM dws.dws_user_first_recharge_retention_d_h
WHERE dt >= '2026-02-24' GROUP BY dt HAVING fr=0 AND d1>0;
-- 结果：空
```

---

## 5. 差异归因（不改 SQL）

| 指标 | 差异级别 | 归因 |
|------|----------|------|
| LTV new_users（5 月） | 0~7 人/日 | cohort：`dim_user_all` vs `dwd_user_register_d_v2` |
| LTV new_users（3 月初） | 100~200 人/日 | 同上，测试环境早期两源偏差大 |
| LTV day_0 金额 | 0~931 元/日 | cohort 用户集合 + 维度拆行差异 |
| 首充 cohort | 一致 | — |
| 首充 day1 | +1~+13 | 活跃：`user_d_h` bitmap vs `page_view` |
| 首充 day1（05-24） | 47 vs NULL | 未成熟窗：旧表 ETL 写 NULL，`_h` 存 bitmap + VIEW CASE WHEN |

---

## 6. 复现 SQL

```sql
-- LTV new_users 日对比
SELECT h.dt, h.h_new, o.o_new, h.h_new-o.o_new diff
FROM (SELECT dt, SUM(BITMAP_COUNT(new_users)) h_new FROM dws.dws_user_reg_ltv_d_h GROUP BY dt) h
JOIN (SELECT dt, SUM(new_users) o_new FROM dws.dws_user_reg_ltv_daily_d GROUP BY dt) o ON h.dt=o.dt
ORDER BY h.dt;

-- LTV day0 金额（_h 元 vs 旧表分/100）
SELECT h.dt, h.h_d0, o.o_d0, h.h_d0-o.o_d0 diff
FROM (SELECT dt, SUM(day_0_pay_amount) h_d0 FROM dws.dws_user_reg_ltv_d_h GROUP BY dt) h
JOIN (SELECT dt, SUM(day_0_pay_amount)/100 o_d0 FROM dws.dws_user_reg_ltv_daily_d GROUP BY dt) o ON h.dt=o.dt
ORDER BY h.dt;

-- 首充 cohort + day1
SELECT h.dt, h.h_fr, o.o_fr, h.h_d1, o.o_d1
FROM (
  SELECT dt, SUM(BITMAP_COUNT(first_recharge_users)) h_fr,
         SUM(BITMAP_COUNT(day1_ret_cnt)) h_d1
  FROM dws.dws_user_first_recharge_retention_d_h GROUP BY dt
) h
JOIN (
  SELECT dt, SUM(first_recharge_users) o_fr, SUM(day1_ret_cnt) o_d1
  FROM dws.dws_user_first_recharge_retention_d GROUP BY dt
) o ON h.dt=o.dt ORDER BY h.dt;
```

---

## 7. 判定

| 检查项 | 结果 |
|--------|------|
| 补数覆盖（有效区间） | 通过 |
| 首充 cohort 与 dim / 旧表 | 通过 |
| LTV new_users 5 月日汇总 | 通过（≤7 人/日） |
| LTV day0 金额 5 月中下旬 | 基本通过（05-15 后 9/10 天一致） |
| 首充 day1 vs 旧表 | **预期差异**（活跃口径升级） |
| 数据质量异常（fr=0,d1>0） | 通过 |

**建议**：保持现有 SQL；生产切流前建兼容 VIEW，下游读 VIEW 获得未成熟 NULL 口径。
