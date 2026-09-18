# user_type 大写化 · C 类 6 表 test 发版参数

**提交人**: 又初 · 2026-06-29  
**环境**: test 海豚 · project=运营系统  
**project_code**: `20524869250304`  
**prod**: 未发（等 A 类+dim 协调）

## 改法口径

`COALESCE(NULLIF(TRIM(user_type),''),'normal'/'unknown')`  
→ `COALESCE(NULLIF(TRIM(UPPER(user_type)),''),'NORMAL'/'UNKNOWN')`

## 9 个 task（test 已 publish）

| # | 表 | task_name | wf_code | wf_name | task_code | 仓库 SQL |
|---|-----|-----------|---------|---------|-----------|----------|
| 1 | dws.dws_user_promotion_behavior_d | dws_user_promotion_behavior_d | 21869820474368 | wf_行为评分_日 | 174798587812672 | ops_system/04.dws/dws_user_promotion_behavior_d/dws_user_promotion_behavior_d.sql |
| 2 | dws.dws_user_promotion_behavior_h | dws_user_promotion_behavior_h | 21869820474368 | wf_行为评分_日 | 174798587812674 | ops_system/04.dws/dws_user_promotion_behavior_h/dws_user_promotion_behavior_h.sql |
| 3 | dws.dws_user_promotion_behavior_h | dws_user_promotion_behavior_h | 21869820474368 | wf_视频汇总_小时 | 174729366771522 | 同上 |
| 4 | dws.dws_user_promotion_behavior_charge_d | dws_user_promotion_behavior_charge_d | 21869770152192 | wf_结算充值_日_首跑 | 174798586849088 | ops_system/04.dws/dws_user_promotion_behavior_charge_d/...sql |
| 5 | dws.dws_user_promotion_behavior_charge_d | dws_user_promotion_behavior_charge_d | 21869770427520 | wf_结算充值_日_补漏 | 174798587303744 | 同上 |
| 6 | dws.dws_user_promotion_behavior_charge_h | dws_user_promotion_behavior_charge_h | 21869770152192 | wf_结算充值_日_首跑 | 174798586849089 | ops_system/04.dws/dws_user_promotion_behavior_charge_h/...sql |
| 7 | dws.dws_user_promotion_behavior_charge_h | dws_user_promotion_behavior_charge_h | 21869770427520 | wf_结算充值_日_补漏 | 174798587303745 | 同上 |
| 8 | ads.ads_keyword_search_hour_d | ads_keyword_search_hour_d_daily | 21869820907264 | wf_ads_日报表_日 | 21946312976896 | ops_system/05.ads/ads_keyword_search_hour_d/ads_keyword_search_hour_d_daily.sql |
| 9 | ads.ads_keyword_search_hour_d | ads_keyword_search_hour_d_hourly | 21869772054016 | wf_用户活跃留存_小时 | 21946311183104 | ops_system/05.ads/ads_keyword_search_hour_d/ads_keyword_search_hour_d_hourly.sql |
| 10 | ads.ads_action_page_funnel_d | ads_action_page_funnel_d | 21869820907264 | wf_ads_日报表_日 | 174729507871557 | ops_system/05.ads/job_ads_action_page_funnel_d/ads_action_page_funnel_d.sql |

> 注：charge/behavior 部分表在 2 个 wf 各有 task（首跑+补漏 / 日+小时），共 **9 个已发布 task**（不含 ads_keyword_search_hour_h_h 衍生 task）。

## test 线 SQL 抽检（live task SQL 已含 UPPER）

`dws_user_promotion_behavior_d` task 174798587812672 末段：

```sql
COALESCE(NULLIF(TRIM(UPPER(r.user_type)), ''), 'NORMAL') AS user_type,
```

## test SR 验证（dt=2026-06-26）

| 表 | user_type 分布 | 说明 |
|----|----------------|------|
| dws_user_promotion_behavior_charge_d | normal=266, vip=31 | **补数前存量仍小写** |
| ads.ads_keyword_search_hour_d | normal=30, vip=18, unknown=9 | **补数前存量仍小写** |
| dws_user_promotion_behavior_d | 0 行 | 该分区未产出/空 |
| ads.ads_action_page_funnel_d | 0 行 | 该分区未产出/空 |

**结论**：test 海豚 **SQL 已 publish 含 UPPER**；分区数据需 **补数跑完** 后才全大写。已触发 06-26 日批 complement，跑完后预期仅 NORMAL/VIP/UNKNOWN。

## 未动

- `ads.ads_keyword_analysis_d_h`（狂人/猫猫收尾）

## git 路径（dev 分支本地已改）

```
ops_system/04.dws/dws_user_promotion_behavior_{d,h}/dws_user_promotion_behavior_*.sql
ops_system/04.dws/dws_user_promotion_behavior_charge_{d,h}/dws_user_promotion_behavior_charge_*.sql
ops_system/05.ads/ads_keyword_search_hour_d/ads_keyword_search_hour_d_{daily,hourly}.sql
ops_system/05.ads/job_ads_action_page_funnel_d/ads_action_page_funnel_d.sql
```
