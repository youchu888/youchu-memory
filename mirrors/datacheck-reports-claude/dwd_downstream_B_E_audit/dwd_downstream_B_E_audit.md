# dwd 下游影响审计 · B订单充值域 + E关键词域

**审计人**: 又初  
**日期**: 2026-06-27  
**环境**: prod（StarRocks 52.221.240.167:9030）  
**基线日**: 2026-06-20（切 _new 前）  
**对比日**: 2026-06-26（切 _new 后）  
**背景**: dwd 主表切至 `dw.dw_user_event_detail_new`（约 06-24/25 上线）

---

## 1. 依赖清单（lineage）

### B · 订单充值域

| 层级 | 表 | 上游 | 状态 |
|------|-----|------|------|
| dwd | dwd_order_paid_d | dw.dw_user_event_detail(_new) | **已切 _new，数据断崖** |
| dwd | dwd_order_paid_h | dw.dw_user_event_detail（旧） | cat4 **未切**，仍正常 |
| dwd | dwd_order_created_d | _new | 分区无数据（疑未跑或未补） |
| dwd | dwd_order_created_h | 旧 | 06-24 起断崖（466→1） |
| dwm | dwm_order_paid_d | dwd_order_paid_d | 随 d 表 |
| dwm | dwm_user_order_d_d | dwd_order_paid_d | 随 d 表 |
| dws | dws_app_order_d | order_created_h + **order_paid_d** | **支付侧断崖** |
| dws | dws_user_finance_d | dwd_order_paid_d + coin_consume_h | 充值侧随 d 表 |
| dws | dws_settlement_detail | 小时 Flink 结算流 | **独立管道，正常** |
| dws | dws_user_promotion_behavior_charge_d | settlement_detail | **正常**（读 settlement 非 dwd_d） |
| dws | dws_user_promotion_behavior_d | settlement + 多源 | 06-24 后 cnt 骤降（疑依赖 order 域） |
| ads | ads_recharge_composition_d | — | prod 无此表 |

### E · 关键词域

| 层级 | 表 | 上游 | 状态 |
|------|-----|------|------|
| dwd | dwd_keyword_search_d | **dw_user_event_detail_new** | daily 已切，有量 |
| dwd | dwd_keyword_click_d | **dw_user_event_detail_new** | daily 已切，有量 |
| dwd | dwd_keyword_search_h | 旧 detail | cat4 **未切** |
| dwm | dwm_keyword_search_app_d / dwm_keyword_click_app_d | dwd_*_d | prod **无分区数据** |
| ads | ads_keyword_analysis_d_d | search_h + click_d | prod **无数据**（疑 job 未跑或读 _h） |
| ads | ads_keyword_search_stats_d / summary_d | — | prod **无数据** |

---

## 2. 前后对账（06-20 vs 06-26）

### B · 订单充值

| 指标 | 06-20 | 06-26 | 判定 |
|------|-------|-------|------|
| dwd_order_paid_d 行数 | 222 | 2 | **BUG** |
| dwd_order_paid_h 行数 | — | 2（26日）/ 159（24日） | _h 未切仍正常 |
| dw 源 order_paid（24日） | old=195 | new=1 | **根因：_new 源 ingest 断层** |
| order_type 分布 | coin_purchase+vip_subscription 小写 | 仍小写 | 非大写化问题 |
| dws_settlement order_paid | ~186/日 | ~171/日 | 合理 |
| dws_promotion_charge_d | ~193 行/23600元 | ~297 行/21065元 | 合理（走 settlement） |
| dws_app_order_d 行数 | 403 | 5 | **BUG**（读 order_paid_d） |

### E · 关键词

| 指标 | 06-20 | 06-26 | 判定 |
|------|-------|-------|------|
| dwd_keyword_search_d | 394 | 333 | 合理波动 |
| dwd_keyword_click_d | 47 | 161 | 合理 |
| event 字段 | keyword_search 小写 | keyword_search 小写 | 无大写化 |
| click_item_type_key | video/comic **小写** | LONG_VIDEO/VIDEO/COMIC **大写** | **schema 变更** |
| dw 源 keyword_search（20日） | old=557860 | new=2984 | _new 过滤后仍支撑 dwd 产出 |

---

## 3. 问题清单（表 | 问题 | 影响 | 修法）

| 表 | 问题 | 影响 | 修法 |
|----|------|------|------|
| dw.dw_user_event_detail_new | order_paid 事件 06-24 仅 1 条 vs old 195 | dwd_order_paid_d 断崖，下游 dws_app_order_d 支付指标归零 | **P0** 查 Flink/ingest 为何 _new 丢 order_paid；切正前勿以 d 表做结算报表 |
| dwd.dwd_order_paid_d | 06-23 起 cnt 1~3/日 | 所有读 _d 的 dwm/dws/ads 充值指标失真 | 源修复后 T-1 补数；或临时回读 old detail |
| dwd.dwd_order_created_h | 06-24 起 1~20/日 vs 前 400+ | dws_app_order_d 创建侧断崖 | 查 _h 是否误切 _new 或 ingest；未切 cat4 标待审 |
| dws.dws_app_order_d | 支付 cnt/amt 随 order_paid_d 归零 | APP 订单日报失真 | 源修复 + 补数；或改读 settlement/order_paid_h 过渡 |
| dws.dws_user_finance_d | recharge 随 order_paid_d | 用户财务日表充值偏低 | 同上 |
| dwd.dwd_keyword_click_d | click_item_type_key 06-26 为大写枚举 | ads 硬编码 `= 'VIDEO'` 仅匹配部分（LONG_VIDEO 漏计） | dwd ETL 对齐 _h 的 CASE 归一化；或 ads 改 LIKE/IN 全集 |
| ads.ads_keyword_analysis_d_d | prod 无分区 | 关键词分析报表空 | 确认海豚 job + 上游改读 search_d；补 T-1 |
| dwm.dwm_keyword_* | prod 无数据 | 中间层断流 | 查调度是否启用 |
| dwd_order_paid_h / keyword_*_h | cat4 未切正 | 读 _h 下游暂不受影响 | 标「未切待审」，切正后复跑本审计 |

---

## 4. 大写化 pattern 核查结论

- **order_type**：06-19/06-26 均为小写 `coin_purchase`/`vip_subscription` → B 域**非**大写化致 bug，是 **源表断层**。
- **event**：keyword_search/click、order_paid 均小写 → 硬编码小写 event 过滤**未被打挂**。
- **click_item_type_key**（E 域）：06-19 小写 `video`→06-26 大写 `VIDEO/LONG_VIDEO/...`；ads ETL 期望 `VIDEO/COMIC/NOVEL` 大写 → **部分匹配**（video 变 LONG_VIDEO 漏计），属 schema/归一化问题，非全面大写化。

---

## 5. 合理 vs BUG 汇总

| 判定 | 项 |
|------|-----|
| **BUG** | order_paid_d 断崖、dws_app_order_d 支付侧、order_created_h 断崖、click_item_type 归一化不一致 |
| **合理** | settlement/charge_d 仍正常；keyword search/click 日表量级；order_type 小写稳定 |
| **待审/未切** | cat4 小时表 + cat5 temp 双跑；读 _h 下游切正后再验 |

---

## 变更记录

- 2026-06-27 又初：首版 prod 审计，覆盖 bus#111/#115/#119/#123/#126 派单
