# A1 FULL JOIN · ads_channel_summary_d · test · 2026-11-12

## 总量

| src | rows | new_user | recharge | d1_ret | d7_ret | lp_new |
|---|---:|---:|---:|---:|---:|---:|
| shadow | 1366 | 5988 | 3367282 | 45 | 0 | 0 |
| formal | 587 | 2278 | 1722282 | 88 | 34 | 0 |

## 全键分类（app_id×channel）

| 类 | 键数 | 说明 |
|---|---:|---|
| equal | 291 | 关键指标一致 |
| metric_diff | 257 | 同键指标差（new 行差 225 / install 167 / lp_click 149 / d1n 128 / ad_click 113 / recharge 35 / d1r 26 / d7r 11） |
| only_shadow | 818 | 影子有正式无（多为结算侧渠道展开；only_shadow 侧 new 合计约 198） |
| only_formal | 39 | 正式有影子无 |

闭合：only_shadow+equal+metric_diff=1366；only_formal+equal+metric_diff=587。

## 成因（按设计预期，非静默错）

1. **留存源更换**：影子读 `dws_app_retention_d_h`；正式海豚仍读作废/旧 channel_retention → d1/d7 差属预期。
2. **结算源覆盖更宽**：影子 `dws_app_channel_summary_d_d` 全渠道 JOIN → only_shadow 键多、new/recharge 高于正式。
3. **落地页新客空源**：两边 `lp_new=0`（`dws_register_by_landing_page_d_d` 未建，ETL 空源）。
4. **配置类差**：渠道集合与正式海豚过滤不一致，归 only_* / metric_diff，切产前需业务确认是否接受「跟结算日表全量」。

## 判定

- 链路可跑：ETL+pb SUCCESS。
- 对账**未平**；差已分类闭合，属换源/覆盖预期，**不按百分比报核过**。
- 交审：附本报告；产编排仍交狂人。

## 2026-11-16 样本补强（交审用）

### only_* 合计

| 类 | 键数 | new 合计 | recharge 合计 |
|---|---:|---:|---:|
| only_formal | 39 | 4 | 5000（HDXY-015/test） |
| only_shadow | 818 | 198 | 184000 |

### only_formal 特征

- 多为 **organic / 测试渠道** 上的零指标键；new 合计仅 4（YC-161/DFA-05/JHA-208 organic）。
- 正式有、结算日表无 → 影子不展开；切产若「跟结算全量」可接受丢这 39 键。

### only_shadow 头样（new 降序）

| app_id | channel | new | install |
|---|---|---:|---:|
| SEO-002 | organic | 82 | 0 |
| WYYL-104 | Gsences | 26 | 0 |
| YC-001 | oufz1tx 等 | 3～4 | 0～6 |

### metric_diff 头样（|Δnew| 最大）

影子 new ≫ 正式（正式常为 0）：YC-001/organic +724、JHA-3002/organic +462、YC-001 多渠道 +59～151。  
与「结算日表全渠道覆盖更宽」一致；d1r/d7r 在这些头样上多为 0/0（留存差另见留存源更换）。

### 交审结论（建议）

1. **接受「跟结算日表全量」** → A1 可挂产影子并行；only_formal 39 键可忽略。  
2. **必须对齐旧海豚过滤集合** → 需加渠道/产品白名单，再重跑对账。  
3. 落地页新客两边仍空源，不挡本表挂影子。
