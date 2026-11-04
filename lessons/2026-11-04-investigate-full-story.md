---
date: 2026-11-04
tags: [datacheck, root-cause, promotion, process]
severity: high
domain: datacheck
---

# 查异常要把来龙去脉查清：ads 行 → ETL → 渠道日明细 → 上游覆盖

## 背景

产品月表 `ads_product_promotion_summary_m`：DX-145 / dept 89 / 2026-08，次留人数 987 > 新增 734。

## 坑 / 错误做法

停在「次留与新增口径可能不同」或只对产品级结算总量，不拆渠道日、不核各上游有数起点。

## 正确做法

1. 核 ads 行与截图一致  
2. 读月/周 ETL：新增=结算 `dws_app_channel_summary_d_d`，次留=`dws_app_retention_d_h`，同推广窗  
3. 落到唯一渠道 `FMFzmkcW`，按日对比 new vs day1_ret  
4. 发现结算自 08-12 才有；推广自 08-05；08-05～11 次留 822、新增 0；重叠段 165≪734  
5. 差额验算：822+165=987  

结论：上游覆盖不齐导致的汇总假异常，非 day1 公式当日记错。

## 验证

分段合计能加回月表两字段；重叠日 ret≤new。

## 关联

- feedback：`feedback_investigate_full_story.md`
- 表：`ads.ads_product_promotion_summary_m`；渠道维 `dim.dim_channel_info_all`
