# 指标库 · ads+dws 覆盖对照表

> 生成：2026-09-22 · **只读盘点，未改库**
> 表/列：prod StarRocks information_schema（全量）
> 指标实现：test metadata `metric_implementation`（active）
> 已排除：shadow / bak / tmp / probe / poc / `_old` / 日期备份 / zz_drop 等
> 「online」= 现网仍存在的正式表

## 总览

| 项 | 数 |
|----|----|
| 正式表（ads+dws） | 112 |
| 其中空表 | 14 |
| 已挂满 | 21 |
| 部分挂 | 16 |
| 未挂 | 75 |
| 疑似指标列合计 | 1399 |
| 尚未挂上的疑似列 | 990 |
| concept published / orphaned | 301 / 11 |
| active implementation | 419 |
| 排除的影子/备份表 | 35 |

## 人话结论

1. 现网正式表 **112** 张；已挂/部分挂 **37** 张，完全没挂 **75** 张。
2. 启发式估还有约 **990** 个疑似指标列没进库。
3. 实现上的表名都能在现网对上（无「挂飞」）；但存在新旧并存（如 `dws_app_user_d` 已挂、现网主力 `dws_app_user_d_h` 未挂）——填数时按现网主力表补，旧空表可后置。

## 建议第一批：活跃域

| 表 | 状态 | 疑似列 | 已挂实现 | 未挂列 | 约行数 |
|----|------|--------|----------|--------|--------|
| `dws.dws_session_duration_device_d` | 未挂 | 7 | 0 | 7 | 0 |
| `dws.dws_session_duration_user_d` | 未挂 | 7 | 0 | 7 | 13,837,526 |
| `dws.dws_app_user_d_h` | 未挂 | 5 | 0 | 5 | 551,081,797 |
| `dws.dws_app_user_m_d_new` | 未挂 | 5 | 0 | 5 | 35,218,292 |
| `dws.dws_app_user_w_d_new` | 未挂 | 5 | 0 | 5 | 72,464,178 |
| `dws.dws_source_analysis_active_d` | 未挂 | 2 | 0 | 2 | 63,232 |
| `ads.ads_app_metrics_hourly_d` | 部分挂 | 36 | 12 | 24 | 3,471,416 |
| `ads.ads_app_metrics_daily_d` | 部分挂 | 48 | 31 | 22 | 175,556 |
| `ads.ads_app_active_summary` | 已挂 | 2 | 2 | 0 | 837 |
| `ads.ads_app_summary_d` | 已挂 | 9 | 10 | 0 | 184,204 |
| `dws.dws_app_channel_dau_d` | 已挂 | 3 | 3 | 0 | 37,770,843 |
| `dws.dws_app_user_d` | 已挂 | 5 | 5 | 0 | 0 |
| `dws.dws_app_user_m` | 已挂 | 5 | 5 | 0 | 0 |
| `dws.dws_app_user_w` | 已挂 | 5 | 5 | 0 | 0 |

## 未挂表 TOP（按疑似列数）

| 表 | 疑似列 | 总列 | 约行数 |
|----|--------|------|--------|
| `dws.dws_app_event_funnel_d_d` | 55 | 60 | 87,213 |
| `ads.ads_source_analysis_metric_d` | 39 | 43 | 63,245 |
| `dws.dws_user_tag_d_d` | 37 | 53 | 1,537,781,445 |
| `dws.dws_user_tag_d` | 36 | 53 | 240,756,919 |
| `dws.dws_source_analysis_ltv_d` | 34 | 38 | 63,231 |
| `dws.dws_user_reg_ltv_d_h` | 32 | 38 | 215,539,954 |
| `dws.dws_app_retention_d_h` | 31 | 37 | 279,560,067 |
| `dws.dws_user_first_recharge_retention_d_h` | 31 | 37 | 5,832,480 |
| `ads.ads_user_base_daily_d` | 30 | 32 | 66,422 |
| `dws.dws_source_analysis_retention_d` | 30 | 34 | 63,226 |
| `dws.dws_user_base_daily_d` | 30 | 32 | 190,003 |
| `ads.ads_video_operation_stats_d` | 28 | 31 | 32,547 |
| `ads.ads_app_fake_register_d_d` | 23 | 33 | 18,976 |
| `dws.dws_channel_funnel_other_d` | 18 | 22 | 1,784,188 |
| `ads.ads_landing_page_metrics_d_h` | 17 | 22 | 2,083,432 |
| `ads.ads_register_attribution_board_d_d` | 17 | 22 | 8,517 |
| `ads.ads_product_report_metric_d_d` | 16 | 22 | 63,822,779 |
| `ads.ads_content_rank_m_d` | 13 | 24 | 482,249,133 |
| `ads.ads_content_rank_w_d` | 13 | 24 | 1,258,514,295 |
| `dws.dws_app_order_d_h` | 13 | 20 | 9,735,997 |
| `dws.dws_video_account_d_d` | 13 | 20 | 1,032,574,059 |
| `dws.dws_video_device_d_d` | 13 | 19 | 960,621,900 |
| `ads.ads_content_rank_d_d` | 12 | 21 | 5,017,280,493 |
| `dws.dws_register_attribution_metrics_d_d` | 12 | 15 | 52 |
| `dws.dws_user_retention_d` | 12 | 15 | 6,795,256 |
| `ads.ads_app_video_funnel_d` | 11 | 14 | 31,530 |
| `ads.ads_user_region_geo_d` | 11 | 18 | 59,659,394 |
| `ads.ads_video_funnel_d` | 11 | 15 | 993,696,232 |
| `ads.ads_keyword_analysis_d_h` | 10 | 16 | 1,559,848,658 |
| `dws.dws_app_page_visit_d_d` | 10 | 15 | 53,237,492 |

## 部分挂 TOP（按未挂列数）

| 表 | 已挂实现 | 未挂列 | 未挂样例 |
|----|----------|--------|----------|
| `ads.ads_app_metrics_hourly_d` | 12 | 24 | hr,new_reg_ids,new_reg_channel_ids,new_reg_nature_ids,new_reg_ios_ids,new_reg_android_ids,new_reg_pc_ids,new_reg_other_ids,login_all_ids,login_ios_ids |
| `ads.ads_channel_metrics_daily_d` | 18 | 24 | login_all_ids,login_ios_ids,login_android_ids,login_pc_ids,login_other_ids,dau_ids,dau_ios_ids,dau_android_ids,dau_pc_ids,dau_other_ids |
| `ads.ads_app_metrics_daily_d` | 31 | 22 | new_reg_ids,new_reg_channel_ids,new_reg_nature_ids,new_reg_ios_ids,new_reg_android_ids,new_reg_pc_ids,new_reg_other_ids,login_all_ids,login_ios_ids,login_android_ids |
| `dws.dws_channel_daily_funnel_d` | 9 | 16 | device_type,video_media_bm,novel_id_bm,comic_id_bm,play_video_count,play_novel_count,play_comic_count,video_play_progress_ratio,novel_play_progress_ratio,comic_play_progress_ratio |
| `ads.ads_product_day_stat_d` | 41 | 11 | effective_dau_count,effective_old_dau_count,effective_new_reg_count,effective_chl_new_reg_count,effective_nat_new_reg_count,login_user_count,non_guest_reg_count,video_play_cnt,ad_impression_cnt,ad_click_cnt |
| `dws.dws_user_promotion_behavior_h` | 2 | 9 | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount,consume_amount,is_video_viewer,total_play_time,is_payer,is_order_creator |
| `dws.dws_app_order_d` | 6 | 7 | order_type,order_pay_cnt,order_pay_amt,new_order_pay_users,new_order_pay_amt,old_order_pay_cnt,old_order_pay_amt |
| `dws.dws_user_promotion_behavior_d` | 5 | 6 | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount,is_payer,is_order_creator |
| `dws.dws_recharge_composition_user_h` | 4 | 4 | register_time,register_date,user_type_source,recharge_user_flag |
| `dws.dws_user_promotion_behavior_charge_h` | 1 | 4 | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount |
| `ads.ads_page_heatmap_d` | 4 | 2 | x,y |
| `dws.dws_app_channel_summary_h` | 11 | 2 | new_user_ios,new_user_android |
| `ads.ads_channel_daily_funnel_report_d` | 21 | 1 | device_type |
| `dws.dws_app_channel_deduction_d` | 9 | 1 | new_user |
| `dws.dws_app_channel_deduction_h` | 9 | 1 | new_user |
| `dws.dws_user_promotion_behavior_charge_d` | 4 | 1 | register_date |

## 全表明细

| 库 | 表 | 状态 | 总列 | 疑似指标 | 已挂实现 | concept | 未挂列 | 空表 | 未挂样例 |
|----|----|------|------|----------|----------|---------|--------|------|----------|
| dws | `dws_app_event_funnel_d_d` | 未挂 | 60 | 55 | 0 | 0 | 55 |  | device_type,app_install_user_cnt,app_install_session_cnt,app_install_event_cnt,user_register_user_cnt,user_register_session_cnt,user_register_event_cnt,user_login_user_cnt,user_login_session_cnt,user_login_event_cnt |
| ads | `ads_source_analysis_metric_d` | 未挂 | 43 | 39 | 0 | 0 | 39 |  | new_user_cnt,day1_ret_cnt,day6_ret_cnt,day14_ret_cnt,day29_ret_cnt,active_user_30d,day_0_pay_amount,day_1_pay_amount,day_2_pay_amount,day_3_pay_amount |
| dws | `dws_user_tag_d_d` | 未挂 | 53 | 37 | 0 | 0 | 37 |  | last_3_login_day,last_7_login_day,last_15_login_day,last_30_login_day,is_play,last_3_video_day,last_7_video_day,last_15_video_day,last_30_video_day,last_3_video_count |
| dws | `dws_user_tag_d` | 未挂 | 53 | 36 | 0 | 0 | 36 |  | last_3_login_day,last_7_login_day,last_15_login_day,last_30_login_day,is_play,last_3_video_day,last_7_video_day,last_15_video_day,last_30_video_day,last_3_video_count |
| dws | `dws_source_analysis_ltv_d` | 未挂 | 38 | 34 | 0 | 0 | 34 |  | new_users,day_0_pay_amount,day_1_pay_amount,day_2_pay_amount,day_3_pay_amount,day_4_pay_amount,day_5_pay_amount,day_6_pay_amount,day_7_pay_amount,day_8_pay_amount |
| dws | `dws_user_reg_ltv_d_h` | 未挂 | 38 | 32 | 0 | 0 | 32 |  | new_users,day_0_pay_amount,day_1_pay_amount,day_2_pay_amount,day_3_pay_amount,day_4_pay_amount,day_5_pay_amount,day_6_pay_amount,day_7_pay_amount,day_8_pay_amount |
| dws | `dws_app_retention_d_h` | 未挂 | 37 | 31 | 0 | 0 | 31 |  | new_users,day1_ret_cnt,day2_ret_cnt,day3_ret_cnt,day4_ret_cnt,day5_ret_cnt,day6_ret_cnt,day7_ret_cnt,day8_ret_cnt,day9_ret_cnt |
| dws | `dws_user_first_recharge_retention_d_h` | 未挂 | 37 | 31 | 0 | 0 | 31 |  | first_recharge_users,day1_ret_cnt,day2_ret_cnt,day3_ret_cnt,day4_ret_cnt,day5_ret_cnt,day6_ret_cnt,day7_ret_cnt,day8_ret_cnt,day9_ret_cnt |
| ads | `ads_user_base_daily_d` | 未挂 | 32 | 30 | 0 | 0 | 30 |  | user_ids,vip_user_ids,non_vip_ids,dormancy_light_ids,dormancy_light_vip_ids,dormancy_light_no_vip_ids,dormancy_medium_ids,dormancy_medium_vip_ids,dormancy_medium_no_vip_ids,dormancy_deep_ids |
| dws | `dws_source_analysis_retention_d` | 未挂 | 34 | 30 | 0 | 0 | 30 |  | new_users,day1_ret_cnt,day2_ret_cnt,day3_ret_cnt,day4_ret_cnt,day5_ret_cnt,day6_ret_cnt,day7_ret_cnt,day8_ret_cnt,day9_ret_cnt |
| dws | `dws_user_base_daily_d` | 未挂 | 32 | 30 | 0 | 0 | 30 |  | user_ids,vip_user_ids,non_vip_ids,dormancy_light_ids,dormancy_light_vip_ids,dormancy_light_no_vip_ids,dormancy_medium_ids,dormancy_medium_vip_ids,dormancy_medium_no_vip_ids,dormancy_deep_ids |
| ads | `ads_video_operation_stats_d` | 未挂 | 31 | 28 | 0 | 0 | 28 |  | video_view_cnt,video_view_wow,video_play_cnt,video_play_wow,play_click_rate,play_click_rate_wow,play_complete_cnt,valid_view_count,valid_view_rate,valid_view_rate_wow |
| ads | `ads_app_fake_register_d_d` | 未挂 | 33 | 23 | 0 | 0 | 23 |  | hit_rule_cnt,reg_uid,susp_uid,susp_rate,confidence,r1_burst_uid,r4_ipdom_uid,r3_lbburst_uid,r2_farm_uid,ip_cnt |
| dws | `dws_channel_funnel_other_d` | 未挂 | 22 | 18 | 0 | 0 | 18 |  | device_type,novel_play_device_bm,comic_play_device_bm,novel_id_bm,comic_id_bm,play_novel_count,play_comic_count,novel_play_progress_ratio,comic_play_progress_ratio,pay_uid_bm |
| ads | `ads_landing_page_metrics_d_h` | 未挂 | 22 | 17 | 0 | 0 | 17 |  | landing_page_view_num,landing_page_view_ip_num,landing_page_click_ip_num,landing_page_download_num,landing_page_download_ip_num,install_num,deduction_install_num,register_num,deduction_register_num,vip_charge_users |
| ads | `ads_register_attribution_board_d_d` | 未挂 | 22 | 17 | 0 | 0 | 17 |  | eligible_register_cnt,has_candidate_cnt,attribution_success_cnt,high_confidence_cnt,rewrite_success_cnt,rewrite_fail_cnt,rewrite_skipped_cnt,rewrite_not_writeback_cnt,rewrite_unknown_cnt,score_lt60_cnt |
| ads | `ads_product_report_metric_d_d` | 未挂 | 22 | 16 | 0 | 0 | 16 |  | install_num,new_uid_cnt,active_uid_cnt,login_uid_cnt,launch_cnt,session_cnt,session_dur_sec_sum,daily_dur_sec_sum,daily_uid_cnt,revenue_cny_fen |
| ads | `ads_content_rank_m_d` | 未挂 | 24 | 13 | 0 | 0 | 13 |  | month_no,view_cnt,view_uv,like_cnt,collect_cnt,comment_cnt,purchase_cnt,sum_play_ms,play_cnt,play_cnt_raw |
| ads | `ads_content_rank_w_d` | 未挂 | 24 | 13 | 0 | 0 | 13 |  | week_no,view_cnt,view_uv,like_cnt,collect_cnt,comment_cnt,purchase_cnt,sum_play_ms,play_cnt,play_cnt_raw |
| dws | `dws_app_order_d_h` | 未挂 | 20 | 13 | 0 | 0 | 13 |  | order_type,order_create_users,order_create_cnt,order_create_amt,order_pay_users,order_pay_cnt,order_pay_amt,new_order_pay_users,new_order_pay_cnt,new_order_pay_amt |
| dws | `dws_video_account_d_d` | 未挂 | 20 | 13 | 0 | 0 | 13 |  | play_count,view_count,total_play_duration,watch_account_count,complete_count,bounce_count,video_like_count,video_comment_count,video_collect_count,purchase_count |
| dws | `dws_video_device_d_d` | 未挂 | 19 | 13 | 0 | 0 | 13 |  | play_count,view_count,total_play_duration,watch_device_count,complete_count,bounce_count,video_like_count,video_comment_count,video_collect_count,purchase_count |
| ads | `ads_content_rank_d_d` | 未挂 | 21 | 12 | 0 | 0 | 12 |  | view_cnt,view_uv,like_cnt,collect_cnt,comment_cnt,purchase_cnt,sum_play_ms,play_cnt,play_cnt_raw,play_uv |
| dws | `dws_register_attribution_metrics_d_d` | 未挂 | 15 | 12 | 0 | 0 | 12 |  | ios_organic_reg_cnt,has_candidate_cnt,attribution_success_cnt,attribution_fail_cnt,high_confidence_cnt,candidate_penetration_rate,attribution_success_rate,high_confidence_rate,rewrite_success_cnt,rewrite_fail_cnt |
| dws | `dws_user_retention_d` | 未挂 | 15 | 12 | 0 | 0 | 12 |  | register_date,new_user_cnt,day1_ret_cnt,day1_ret_rate,day3_ret_cnt,day3_ret_rate,day7_ret_cnt,day7_ret_rate,day15_ret_cnt,day15_ret_rate |
| ads | `ads_app_video_funnel_d` | 未挂 | 14 | 11 | 0 | 0 | 11 |  | view_sid_cnt,play_sid_cnt,valid_sid_cnt,complete_sid_cnt,purchase_sid_cnt,ctr,play_to_valid_rate,valid_to_complete_rate,complete_to_pay_rate,overall_rate |
| ads | `ads_user_region_geo_d` | 未挂 | 18 | 11 | 0 | 0 | 11 |  | country_geonameid,admin1_geonameid,country_iso2,country_name,lat,lon,reg_user_cnt,recharge_amount,ip_bitmap,uid_bitmap |
| ads | `ads_video_funnel_d` | 未挂 | 15 | 11 | 0 | 0 | 11 |  | view_sid_cnt,play_sid_cnt,valid_sid_cnt,complete_sid_cnt,purchase_sid_cnt,ctr,play_to_valid_rate,valid_to_complete_rate,complete_to_pay_rate,overall_rate |
| ads | `ads_keyword_analysis_d_h` | 未挂 | 16 | 10 | 0 | 0 | 10 |  | search_cnt,search_result_cnt,zero_result_search_cnt,search_uv,click_cnt,video_click_cnt,novel_click_cnt,comic_click_cnt,post_click_cnt,conversion_cnt |
| dws | `dws_app_page_visit_d_d` | 未挂 | 15 | 10 | 0 | 0 | 10 |  | pv_cnt,uid_cnt,entry_cnt,jump_cnt,valid_stay_sec_sum,valid_stay_page_cnt,stay_page_cnt,dropout_page_cnt,load_time_sum,load_cnt |
| dws | `dws_register_attribution_result_d` | 未挂 | 35 | 10 | 0 | 0 | 10 |  | register_event_id,register_event_time,score,score_brand,score_model,score_system,score_system_version,score_threshold,time_diff_seconds,time_bucket_max_seconds |
| dws | `dws_user_finance_d` | 未挂 | 14 | 10 | 0 | 0 | 10 |  | recharge_count,recharge_amount,coin_buy_count,coin_buy_amount,vip_buy_count,vip_buy_amount,coin_consume_count,coin_consume_amount,coin_balance_sod,coin_balance_eod |
| dws | `dws_app_coin_consume_d` | 未挂 | 16 | 9 | 0 | 0 | 9 | 是 | consume_users,consume_cnt,consume_qty,new_consume_users,new_consume_cnt,new_consume_qty,old_consume_users,old_consume_cnt,old_consume_qty |
| dws | `dws_app_coin_consume_d_h` | 未挂 | 16 | 9 | 0 | 0 | 9 |  | consume_users,consume_cnt,consume_qty,new_consume_users,new_consume_cnt,new_consume_qty,old_consume_users,old_consume_cnt,old_consume_qty |
| ads | `ads_comic_analysis_account_d` | 未挂 | 15 | 8 | 0 | 0 | 8 |  | show_cnt,view_cnt,complete_cnt,view_uid_bitmap,like_cnt,comment_cnt,collect_cnt,purchase_cnt |
| dws | `dws_user_ltv_d` | 未挂 | 11 | 8 | 0 | 0 | 8 |  | register_date,register_user_cnt,actual_payment_amount_cnt_7,ltv7,actual_payment_amount_cnt_15,ltv15,actual_payment_amount_cnt_30,ltv30 |
| dws | `dws_ad_funnel_metric_d` | 未挂 | 14 | 7 | 0 | 0 | 7 |  | fill_cnt,impression_cnt,click_cnt,close_cnt,skip_cnt,impression_closable_cnt,impression_skippable_cnt |
| dws | `dws_session_duration_device_d` | 未挂 | 15 | 7 | 0 | 0 | 7 | 是 | duration_bucket,session_cnt,device_cnt,duration_sum_sec,avg_session_duration_sec,avg_daily_duration_sec,bounce_cnt |
| dws | `dws_session_duration_user_d` | 未挂 | 16 | 7 | 0 | 0 | 7 |  | duration_bucket,session_cnt,user_cnt,duration_sum_sec,avg_session_duration_sec,avg_daily_duration_sec,bounce_cnt |
| dws | `dws_settlement_detail` | 未挂 | 21 | 7 | 0 | 0 | 7 |  | deduction,amount,coin_amount,payload,order_type,device_id,neg_req_ts |
| ads | `ads_ad_click_user_daily_d` | 未挂 | 8 | 6 | 0 | 0 | 6 |  | history_click_user_ids,today_click_user_ids,history_click_device_ids,today_click_device_ids,new_first_click_user_cnt,new_first_click_device_cnt |
| ads | `ads_ad_space_summary_realtime_d` | 未挂 | 9 | 6 | 0 | 0 | 6 | 是 | exposure_pv,exposure_uv,expose_ip_num,click_pv,click_uv,click_ip_num |
| ads | `ads_ad_summary_d` | 未挂 | 11 | 6 | 0 | 0 | 6 |  | exposure_pv,exposure_uv,expose_ip_num,click_pv,click_uv,click_ip_num |
| ads | `ads_ad_summary_realtime_d` | 未挂 | 10 | 6 | 0 | 0 | 6 | 是 | exposure_pv,exposure_uv,expose_ip_num,click_pv,click_uv,click_ip_num |
| ads | `ads_keyword_search_stats_d` | 未挂 | 10 | 6 | 0 | 0 | 6 |  | search_cnt,search_cnt_wow,click_cnt,click_cnt_wow,search_uv,search_uv_wow |
| ads | `ads_keyword_search_summary_d` | 未挂 | 9 | 6 | 0 | 0 | 6 |  | hot_keyword_cnt,avg_search_depth,search_conv_rate,total_search_cnt,total_search_uv,target_action_uv |
| ads | `ads_user_global_status_all` | 未挂 | 7 | 6 | 0 | 0 | 6 |  | all_device_ids,all_user_ids,all_vip_ids,all_non_vip_ids,reg_user_ids,all_login_ids |
| dws | `dws_channel_funnel_video_d` | 未挂 | 10 | 6 | 0 | 0 | 6 |  | device_type,video_play_device_bm,video_media_bm,play_video_count,video_play_progress_ratio,total_play_duration |
| ads | `ads_channel_promotion_settlement_summary_h` | 未挂 | 14 | 5 | 0 | 0 | 5 | 是 | ip_num,deduction_ip_num,new_user,deduction_new_user,pay_user_num |
| dws | `dws_app_user_d_h` | 未挂 | 12 | 5 | 0 | 0 | 5 |  | new_users,active_users,old_active_users,active_devices,login_users |
| dws | `dws_app_user_m_d_new` | 未挂 | 13 | 5 | 0 | 0 | 5 |  | new_users,active_users,old_active_users,active_devices,login_users |
| dws | `dws_app_user_w_d_new` | 未挂 | 13 | 5 | 0 | 0 | 5 |  | new_users,active_users,old_active_users,active_devices,login_users |
| dws | `dws_dw_table_summary` | 未挂 | 7 | 5 | 0 | 0 | 5 |  | current_data_num,yesterday_data_num,last_7_day_avg_data_num,empty_column_data_num,event_num |
| ads | `ads_channel_promotion_settlement_summary_d` | 未挂 | 10 | 4 | 0 | 0 | 4 |  | ip_num,deduction_ip_num,new_user,deduction_new_user |
| ads | `ads_user_region_stats_d` | 未挂 | 10 | 4 | 0 | 0 | 4 |  | reg_user_cnt,active_user_cnt,vip_active_cnt,normal_active_cnt |
| dws | `dws_user_reg_video_funnel_d_h` | 未挂 | 9 | 4 | 0 | 0 | 4 | 是 | new_users,page_view_user_cnt,video_exposure_user_cnt,first_play_user_cnt |
| ads | `ads_ad_sdk_summary` | 未挂 | 7 | 3 | 0 | 0 | 3 |  | click_num,exposure_num,update_ts |
| ads | `ads_app_info` | 未挂 | 19 | 3 | 0 | 0 | 3 |  | status,enable_signature,ai_ratio |
| ads | `ads_page_behavior_hourly_d` | 未挂 | 8 | 3 | 0 | 0 | 3 |  | hr,uv_count,pv_count |
| dws | `dws_keyword_search_conv_d` | 未挂 | 5 | 3 | 0 | 0 | 3 |  | search_sid_cnt,conv_sid_cnt,search_conv_rate |
| ads | `ads_app_event_data_quality_summary_d` | 未挂 | 5 | 2 | 0 | 0 | 2 |  | num,error_num |
| ads | `ads_user_page_path_name_d_d` | 未挂 | 7 | 2 | 0 | 0 | 2 |  | s_cnt,u_cnt |
| dws | `dws_channel_funnel_page_d` | 未挂 | 6 | 2 | 0 | 0 | 2 |  | device_type,page_display_device_bm |
| dws | `dws_channel_funnel_reg_d` | 未挂 | 6 | 2 | 0 | 0 | 2 |  | device_type,device_id |
| dws | `dws_source_analysis_active_d` | 未挂 | 6 | 2 | 0 | 0 | 2 |  | new_users,active_user_30d |
| ads | `ads_app_event_data_field_err_stats_d` | 未挂 | 6 | 1 | 0 | 0 | 1 |  | num |
| ads | `ads_app_event_statics_h` | 未挂 | 4 | 1 | 0 | 0 | 1 |  | num |
| ads | `ads_keyword_search_hour_d` | 未挂 | 6 | 1 | 0 | 0 | 1 |  | search_cnt |
| ads | `ads_register_attribution_no_candidate_reason_d_d` | 未挂 | 7 | 1 | 0 | 0 | 1 |  | register_cnt |
| ads | `ads_video_tag_heat_daily_d` | 未挂 | 6 | 1 | 0 | 0 | 1 |  | heat_score |
| dws | `dws_ad_error_metric_d` | 未挂 | 9 | 1 | 0 | 0 | 1 |  | error_cnt |
| dws | `dws_ad_request_metric_d` | 未挂 | 6 | 1 | 0 | 0 | 1 |  | request_cnt |
| dws | `dws_settlement_user_register_h` | 未挂 | 11 | 1 | 0 | 0 | 1 |  | register_date |
| dws | `dws_channel_funnel_user_map_d` | 未挂 | 4 | 0 | 0 | 0 | 0 |  |  |
| dws | `dws_data_exception_record_d` | 未挂 | 5 | 0 | 0 | 0 | 0 |  |  |
| ads | `ads_channel_metrics_daily_d` | 部分挂 | 44 | 41 | 18 | 18 | 24 |  | login_all_ids,login_ios_ids,login_android_ids,login_pc_ids,login_other_ids,dau_ids,dau_ios_ids,dau_android_ids,dau_pc_ids,dau_other_ids |
| ads | `ads_app_metrics_hourly_d` | 部分挂 | 38 | 36 | 12 | 12 | 24 |  | hr,new_reg_ids,new_reg_channel_ids,new_reg_nature_ids,new_reg_ios_ids,new_reg_android_ids,new_reg_pc_ids,new_reg_other_ids,login_all_ids,login_ios_ids |
| ads | `ads_app_metrics_daily_d` | 部分挂 | 50 | 48 | 31 | 31 | 22 |  | new_reg_ids,new_reg_channel_ids,new_reg_nature_ids,new_reg_ios_ids,new_reg_android_ids,new_reg_pc_ids,new_reg_other_ids,login_all_ids,login_ios_ids,login_android_ids |
| dws | `dws_channel_daily_funnel_d` | 部分挂 | 29 | 25 | 9 | 9 | 16 |  | device_type,video_media_bm,novel_id_bm,comic_id_bm,play_video_count,play_novel_count,play_comic_count,video_play_progress_ratio,novel_play_progress_ratio,comic_play_progress_ratio |
| ads | `ads_product_day_stat_d` | 部分挂 | 54 | 52 | 41 | 41 | 11 |  | effective_dau_count,effective_old_dau_count,effective_new_reg_count,effective_chl_new_reg_count,effective_nat_new_reg_count,login_user_count,non_guest_reg_count,video_play_cnt,ad_impression_cnt,ad_click_cnt |
| dws | `dws_user_promotion_behavior_h` | 部分挂 | 23 | 11 | 2 | 2 | 9 |  | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount,consume_amount,is_video_viewer,total_play_time,is_payer,is_order_creator |
| dws | `dws_app_order_d` | 部分挂 | 20 | 13 | 6 | 6 | 7 | 是 | order_type,order_pay_cnt,order_pay_amt,new_order_pay_users,new_order_pay_amt,old_order_pay_cnt,old_order_pay_amt |
| dws | `dws_user_promotion_behavior_d` | 部分挂 | 22 | 11 | 5 | 5 | 6 |  | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount,is_payer,is_order_creator |
| dws | `dws_recharge_composition_user_h` | 部分挂 | 16 | 8 | 4 | 4 | 4 |  | register_time,register_date,user_type_source,recharge_user_flag |
| dws | `dws_user_promotion_behavior_charge_h` | 部分挂 | 12 | 5 | 1 | 1 | 4 |  | register_date,vip_charge_amount,deduction_vip_charge_amount,coin_charge_amount |
| dws | `dws_app_channel_summary_h` | 部分挂 | 16 | 13 | 11 | 11 | 2 |  | new_user_ios,new_user_android |
| ads | `ads_page_heatmap_d` | 部分挂 | 10 | 6 | 4 | 4 | 2 |  | x,y |
| ads | `ads_channel_daily_funnel_report_d` | 部分挂 | 26 | 22 | 21 | 21 | 1 |  | device_type |
| dws | `dws_app_channel_deduction_d` | 部分挂 | 13 | 10 | 9 | 9 | 1 |  | new_user |
| dws | `dws_app_channel_deduction_h` | 部分挂 | 13 | 10 | 9 | 9 | 1 |  | new_user |
| dws | `dws_user_promotion_behavior_charge_d` | 部分挂 | 11 | 5 | 4 | 4 | 1 |  | register_date |
| dws | `dws_user_reg_ltv_daily_d` | 已挂 | 38 | 32 | 32 | 32 | 0 | 是 |  |
| dws | `dws_app_retention_d` | 已挂 | 37 | 31 | 31 | 31 | 0 | 是 |  |
| dws | `dws_user_first_recharge_retention_d` | 已挂 | 37 | 31 | 31 | 31 | 0 | 是 |  |
| ads | `ads_channel_promotion_summary_d` | 已挂 | 21 | 17 | 17 | 17 | 0 |  |  |
| ads | `ads_user_retention_d` | 已挂 | 21 | 17 | 18 | 18 | 0 | 是 |  |
| ads | `ads_channel_promotion_summary_h` | 已挂 | 18 | 15 | 15 | 15 | 0 |  |  |
| dws | `dws_app_channel_summary_d` | 已挂 | 16 | 13 | 13 | 13 | 0 |  |  |
| ads | `ads_channel_summary_d` | 已挂 | 13 | 10 | 10 | 10 | 0 |  |  |
| ads | `ads_user_dormancy_d` | 已挂 | 14 | 10 | 10 | 10 | 0 |  |  |
| ads | `ads_app_summary_d` | 已挂 | 11 | 9 | 10 | 10 | 0 |  |  |
| ads | `ads_action_page_funnel_d` | 已挂 | 12 | 6 | 7 | 7 | 0 |  |  |
| ads | `ads_ad_space_summary_d` | 已挂 | 10 | 6 | 7 | 7 | 0 |  |  |
| dws | `dws_app_user_d` | 已挂 | 12 | 5 | 5 | 5 | 0 | 是 |  |
| dws | `dws_app_user_m` | 已挂 | 13 | 5 | 5 | 5 | 0 | 是 |  |
| dws | `dws_app_user_w` | 已挂 | 13 | 5 | 5 | 5 | 0 | 是 |  |
| dws | `dws_app_channel_retention_d` | 已挂 | 7 | 4 | 4 | 4 | 0 |  |  |
| dws | `dws_user_reg_video_funnel_daily_d` | 已挂 | 9 | 4 | 4 | 4 | 0 |  |  |
| dws | `dws_app_channel_dau_d` | 已挂 | 6 | 3 | 3 | 3 | 0 |  |  |
| ads | `ads_app_active_summary` | 已挂 | 3 | 2 | 2 | 2 | 0 |  |  |
| ads | `ads_user_page_path_d` | 已挂 | 7 | 2 | 2 | 2 | 0 |  |  |
| dws | `dws_register_by_landing_page_d` | 已挂 | 4 | 1 | 1 | 1 | 0 |  |  |

## 下一步（等你点头）

1. 过目未挂/部分挂，标「先做 / 后做 / 不做」（宽表如 `dws_user_tag_d_d` 建议后做）
2. 点头后开第一批：**活跃域** → candidate → D1 定稿
3. 同步纠偏旧表名实现
