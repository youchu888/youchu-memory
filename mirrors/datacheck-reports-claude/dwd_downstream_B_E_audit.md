# DWD 切源下游影响审计 · B 订单充值域 + E 关键词域

> **审计人**：又初 · **环境**：prod StarRocks (52.221.240.167:9030)  
> **日期**：2026-06-27 · **对比窗口**：切前 `2026-06-20` vs 切后 `2026-06-26`  
> **背景**：prod 约 06-24/25 主表切至 `dw.dw_user_event_detail_new`

---

## 0. 执行摘要

| 域 | 总体判定 | 关键结论 |
|----|----------|----------|
| **B 订单充值** | ✅ 合理 | 订单 paid 总量 -4.5%，与结算流一致；无 06-24/25 断崖；channel 有重分配（organic↑）需知悉 |
| **E 关键词** | ✅ 合理（⚠️ 06-22 台阶待观察） | DWD 量降 ~23% 与源表流量同幅；DWD/源捕获率稳定 ~91–95%；抽样 event_id 100% 可回溯 _new |

**铁律遵守**：废弃 `dwd_order_created_d`（prod 无分区数据）、关键词以 `dwd_keyword_search_h` 为准（非废弃 `dwd_keyword_search_d`）。

---

## 1. 依赖清单（Lineage · grep 仓库 ETL）

### 1.1 B 域 · 订单充值

```
dw.dw_user_event_detail          ← 当前 prod ETL 仍读旧表（order 未切 _new）
  ├─ dwd.dwd_order_paid_d
  │    ├─ dws.dws_app_order_d / dws_app_order_d_h
  │    ├─ dws.dws_user_reg_ltv_daily_d / dws_user_reg_ltv_d_h
  │    ├─ dwm.dwm_user_order_d_d / dwm_user_pay_sum_d / dwm_device_order_d_d
  │    └─ dim.dim_user_all
  └─ dwd.dwd_order_created_h     ← 现表（dwd_order_created_d 已废弃/空）
       └─ dws.dws_app_order_d / ads.ads_product_day_stat_d

Flink/Kafka（独立链路，不经 DWD order 表）
  └─ dws.dws_settlement_detail
       ├─ dws.dws_user_promotion_behavior_h      ← 现表（弃用 _d）
       ├─ dws.dws_user_promotion_behavior_charge_h
       └─ ads.ads_channel_summary_d
```

**代码路径**：
- `ops_system/02.dwd/job_dwd_order_type_d/dwd_order_paid_d_daily.sql` → `dw_user_event_detail`
- `ops_system/04.dws/dws_user_promotion_behavior_h/dws_user_promotion_behavior_h.sql` → `dws_settlement_detail`
- `db/dws/结算详情.sql` → settlement routine load

### 1.2 E 域 · 关键词

```
dw.dw_user_event_detail_new      ← 已切（keyword ETL）
  ├─ dwd.dwd_keyword_search_h    ← 现表（小时分区，替代废弃 search_d）
  └─ dwd.dwd_keyword_click_d
       └─ ads.ads_keyword_analysis_d_h
            ├─ ads.ads_keyword_search_hour_d
            └─ dwm.dwm_keyword_search_* / dwm_keyword_click_*
```

**代码路径**：
- `ops_system/02.dwd/dwd_keyword_search_h/dwd_keyword_search_h_daily.sql`
- `ops_system/02.dwd/dwd_keyword_click_d/dwd_keyword_click_d.sql`
- `ops_system/05.ads/ads_keyword_analysis_d_h/ads_keyword_analysis_d_h_daily.sql`

---

## 2. 基线对账（总量 · prod）

### 2.1 B 域

| 表 | 2026-06-20 | 2026-06-26 | Δ | Δ% |
|----|-----------|-----------|---|-----|
| dwd_order_paid_d | 30,404 | 29,041 | -1,363 | -4.5% |
| dwd_order_created_h | 76,834 | 91,805 | +14,971 | +19.5% |
| dws_settlement_detail (order_paid) | 21,324 | 20,368 | -956 | -4.5% |
| dws_user_promotion_behavior_h | 25,623,851 | 21,089,831 | -4,534,020 | -17.7% |
| dws_user_promotion_behavior_charge_h | 6,384,442 | 5,298,002 | -1,086,440 | -17.0% |
| ads_channel_summary_d recharge_amount | 339,630,370 | 338,502,310 | -1,128,060 | -0.3% |
| ads_channel_summary_d new_user | 6,369,515 | 5,309,968 | -1,059,547 | -16.6% |

**日趋势（dwd_order_paid_d）**：06-18~27 在 21k–33k 波动，06-24/25 **无断崖**（06-24=24,470；06-25=25,015；06-26=29,041）。

**源表对照（order_paid · 06-26）**：
- `dw_user_event_detail`：57,858
- `dw_user_event_detail_new`：57,325（-0.9%）
- `dwd_order_paid_d`：29,041（过滤率 ~50%，与切前一致）

### 2.2 E 域

| 表 | 2026-06-20 | 2026-06-26 | Δ | Δ% |
|----|-----------|-----------|---|-----|
| dwd_keyword_search_h | 132,770,760 | 102,787,899 | -29,982,861 | -22.6% |
| dwd_keyword_click_d | 86,467,796 | 62,667,047 | -23,800,749 | -27.5% |
| ads_keyword_analysis_d_h | 6,858,105 | 5,757,056 | -1,101,049 | -16.1% |

**源表对照（keyword_search）**：

| 日期 | old 源 | _new 源 | DWD | DWD/源 |
|------|--------|---------|-----|--------|
| 06-20 | 144,076,001 | — | 132,770,760 | 92.2% vs old |
| 06-26 | 114,004,391 | 112,944,399 | 102,787,899 | 90.2% vs old / **91.0% vs _new** |

**源表对照（keyword_click · 06-26）**：old 70,153,715 · _new 66,106,432（-5.8%）· DWD 62,667,047（**94.8% vs _new**）

**日趋势台阶**：search/click 在 **06-22** 从 ~130M/86M 降至 ~104M/67M 后企稳，**早于** 06-24/25 切源窗口，更像全站流量/过滤变更而非切 _new 单点故障。

---

## 3. app+channel 异常（按 app 独立核算）

### 3.1 B 域 · dwd_order_paid_d（\|Δ\|≥50）

| app_id | channel | pre | post | Δ | pct | 判定 |
|--------|---------|-----|------|---|-----|------|
| JHA-031 | organic | 100 | 1,900 | +1,800 | +1800% | ⚠️ 观察：channel 重分配（原分散渠道→organic），非 0 造假 |
| HX-001 | organic | 49 | 509 | +460 | +939% | ⚠️ 观察：06-26 settlement 该 app 登顶（2,682 笔），与 organic 归并一致 |
| JHA-124 | system | 26 | 392 | +366 | +1408% | ⚠️ 观察 |
| YC-002 | organic | 555 | 305 | -250 | -45% | ✅ 合理波动 |
| JHG-002 | unknown | 199 | 0 | -199 | -100% | ✅ 合理：unknown→其他/organic |
| YC-002 | system | 306 | 116 | -190 | -62% | ✅ 合理 |

**按 app 总量 Top 变化**：YC-002 3730→~3050（-18%）、JHA-204 1664→1318（-21%）与全表 -4.5% 同向，无单 app 断崖。

### 3.2 E 域

全站源表 06-20→06-26 降 ~21%，各 app 同比例收缩；**未发现**单 app 捕获率突变（DWD/源比稳定）。06-22 台阶为跨 app 共性。

---

## 4. 抽样 event_id 验证

[SQL: 从 dwd_keyword_search_h dt=2026-06-26 抽 100 个 event_id，在 dw_user_event_detail_new 回查]

| 抽样 | 命中 |
|------|------|
| 100 / 100 | ✅ 全部存在于 _new 源 |

示例：`00cfdf26fed05ebbb1b92823ae74d144`（DX-001, organic）

---

## 5. 合理 / Bug 判定

### B 域

| 项 | 判定 | 依据 |
|----|------|------|
| dwd_order_paid 总量 | ✅ 合理 | -4.5%，与 settlement order_paid 同幅；无切源日断崖 |
| dwd_order_created vs paid 反向 | ✅ 合理 | created +19.5% / paid -4.5% 属下单-支付漏斗时差，非 DWD bug |
| settlement / promotion 链路 | ✅ 合理 | 独立 Flink 链路，不受 DWD 切 _new 直接冲击；charge 金额 ads 层 -0.3% |
| channel organic 激增 | ⚠️ 观察 | JHA-031/HX-001 等 channel 重分配，疑归因口径优化；建议知秋侧重查 attribution 域 |
| order ETL 未切 _new | ℹ️ 信息 | 仓库仍读旧表；prod 06-26 old/_new order_paid 差 0.9%，切源影响可忽略 |

### E 域

| 项 | 判定 | 依据 |
|----|------|------|
| search DWD=ADS | ✅ 合理 | 06-26 search 102787899 逐位一致 |
| click 总量 DWD→ADS | ✅ 合理 | -0.61% keyword 聚合口径 |
| **video/novel/comic 分类** | **🔴 BUG #5** | 06-25 起 DWD 全大写 VIDEO/NOVEL/COMIC；prod ADS 分类列仍 0（click_cnt 正常）→ 海豚未发版或仍用小写过滤 |
| 全站量 -22~-27% | ✅ 合理 | 业务波动；TJ-053 -99% 疑下线 |
| 06-22 台阶 | ⚠️ 观察 | 全站量级跳变，需与切 _new 解耦 |
| event_id 可追溯 | ✅ 通过 | 抽样 100% 命中 _new |

### 非 Bug（明确排除）

- ❌ 不是 DWD 过滤逻辑突变（捕获率 06-20 vs 06-26 差 <2pp）
- ❌ 不是 0 行误报（各表均有数据；`dwd_order_created_d` 废弃不计）
- ❌ 不是 test 环境数据（sr_prod 52.221.240.167）

---

## 6. 建议跟进

1. **B 域 channel 重分配**：与归因 review 并行，抽 JHA-031/HX-001 的 event_id 对比切前切后 channel 字段。
2. **E 域 06-22 台阶**：查 06-21/06-22 是否有 keyword ETL 过滤/反扒规则上线（与 dwd 主表切 _new 解耦）。
3. **order ETL 切 _new**：仓库 `dwd_order_paid_d_daily.sql` 仍读旧表；切源时 old/_new 差 <1%，可低优先级。

---

## 7. 关键 SQL 索引

```sql
-- B 基线
SELECT dt, COUNT(*) FROM dwd.dwd_order_paid_d
WHERE dt IN ('2026-06-20','2026-06-26') GROUP BY dt;

-- E 基线（现表 _h）
SELECT dt, COUNT(*) FROM dwd.dwd_keyword_search_h
WHERE dt IN ('2026-06-20','2026-06-26') GROUP BY dt;

-- 源表捕获率
SELECT COUNT(*) FROM dw.dw_user_event_detail_new
WHERE dt IN ('2026-06-26','2026-06-27')
  AND event_time >= '2026-06-26 00:00:00' AND event_time < '2026-06-27 00:00:00'
  AND event='keyword_search';
```

---

*报告生成：2026-06-27 17:48 JST · 又初*

---

## 8. 续查 · 06-28 数据 + 下游任务（2026-06-29 prod）

> **环境**：sr_prod 52.221.240.167 · test 海豚查 job（prod 海豚无 MCP 权限）

### 8.1 新鲜度（max dt）

| 表 | max(dt) |
|----|---------|
| dwd_order_paid_d | 2026-06-29 |
| dwd_keyword_search_h | 2026-06-29 |
| dwd_keyword_click_d | 2026-06-29 |
| ads_keyword_analysis_d_h | 2026-06-29 |

### 8.2 06-24~28 日趋势

| 表 | 06-24 | 06-25 | 06-26 | 06-27 | 06-28 | 判定 |
|----|-------|-------|-------|-------|-------|------|
| order_paid_d | 24,470 | 25,015 | 29,041 | 31,004 | 29,384 | ✅ 稳定 |
| keyword_search_h | 102.3M | 99.8M | 102.8M | 117.0M | 116.2M | ✅ 06-27 台阶后企稳 |
| keyword_click_d | 66.7M | 60.6M | 62.7M | 71.4M | 70.2M | ✅ 同向 |
| ads_keyword_analysis_d_h (click_sum) | 66.2M | 60.2M | 62.3M | 71.0M | 69.8M | ✅ 与 DWD 对齐 |
| dws_app_order_d pay_cnt | 24,016 | 25,015 | 28,950 | 30,708 | 29,051 | ✅ |
| settlement order_paid | — | — | — | — | 20,526 | ✅ |

### 8.3 E 域 click_item_type_key（06-28）

`VIDEO` 64.2M / `COMIC` 5.1M / `NOVEL` 0.9M — **已归一化大写**，非 06-26 误报里的 LONG_VIDEO 漏计形态；`ads_keyword_analysis_d_h` click 与 DWD 差 <1%。

### 8.4 下游 job（test 海豚 · 运营系统）

| 工作流 | 06-28 调度 | 06-29 今日 | 备注 |
|--------|-----------|-----------|------|
| wf_dwd_事件明细_日（含 order_paid_d） | SUCCESS 03:20 | SUCCESS 03:20 | ✅ |
| wf_ads_日报表_日（含 ads_keyword_analysis_d_h） | SUCCESS（补跑至 15:48） | SUCCESS 06:20 | 06-27 曾 FAILURE，已恢复 |

**结论**：B+E 域 06-28 **无异常断崖**；E 域 `ads_keyword_analysis_d_h` **有量且与 DWD 一致**（撤回旧误报 subdirectory 报告）。

*续查：2026-06-29 · 又初*

