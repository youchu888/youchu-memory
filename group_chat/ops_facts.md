# 运维事实

群/私聊里「谁对哪张表或哪份 SQL 做了执行」的短事实（建表、重建、DROP、生产执行回执）。
闲聊不进。问「谁重建的 / 谁执行的」时先查本文件，再翻 `learn/` / `archive/`。
每晚 `daily_group_chat_learn.py` 自动追加；人工核实的也可直接补一行。

## 人员速查

| 称呼 / TG | 角色 | 备注 |
|-----------|------|------|
| 王毅 / @wangyi00001 | 大数据运维 | prod/test SR 建表、重建、节点与权限类执行 |
| 希安 / @jiangyan0803 | （群里偶发点名生产执行） | 以当日消息为准 |

## 事实清单

- 2026-08-21 | 私聊 | 执行回执 | 表 dws.dws_app_page_visit_d_d | 用户确认「执行好了」——当日为扩历史分区 ALTER；随后又初继续 prod 补数
- 2026-11-12 | 私聊/bus | 运维已执行 | 表 dws.dws_register_attribution_result_d_paimon_shadow | ALTER 六句（补 rewrite 相关列）运维已跑完；狂人 SHOW COLUMNS 核过 35 列
- 2026-11-17 | 核对补记 | 执行人=运维王毅（@wangyi00001） | 表 dws.dws_app_page_visit_d_d（SR 影子） | B2：uid_cnt bigint→BITMAP，按 `recreate_shadow_uid_bitmap.sql` DROP/CREATE；又初出工单+只读核验，不手改 prod
- 2026-11-16 | 大数据运维群（主人↔王毅互@）+ 私聊收口 | 执行人=王毅 @wangyi00001 | 表 dws.dws_app_page_visit_d_d_paimon_shadow | 跑 recreate_shadow_uid_bitmap.sql（uid_cnt bigint→BITMAP）；主人确认群内互@派执行；19:57 私聊「已经改好了，bitmap」；又初只读 SHOW COLUMNS 核过。问谁重建以此为准，勿写成「对不上是谁」。
- 2026-11-17 | 未知会话 | ｜表 ads_drama_rank_d_d,calc_dt,dws_device_tag_d | 📤 又初→狂人（结案） ──────────── @worker_ant_bot 又初 · 工作簿 2026-11-17 进展（实查 · 口径截至 2026-11-16） 探针时间 2026-11-17 08:45:39 CST · 实查 43s 【簿内主责】 1）设备标签 进展：test `dws_device_tag_d` 最大 calc_dt=2026
- 2026-11-17 | 大数据运维 | 方飞 | 生产SR执行一下, 删除一些过期数据. @wangyi00001
- 2026-11-17 | 大数据运维 | 方飞 | @wangyi00001 生产SR在执行一下这个sql . @wangyi00001
- 2026-11-17 | 未知会话 | ｜表 anna_cute9,b3_behavior_hourly,dim_user_snap | @anna_cute9 查了 dws_user_promotion_behavior_h_h 在两个环境编排里的现状： 1. 依赖探针没改过，生产和测试一模一样：一共 10 个，等前一天的 dim_user_snap 分区，再加 9 张表的水位（结算明细、金币消耗、下单、关键词搜索、广告点击、日间表、支付全表、视频事件小时、SDK 广告点击）。SQL 都是 
- 2026-11-17 | 未知会话 | ｜表 ads_channel_metrics_daily_d,ads_channel_metrics_daily_d_uc,attr_result | 📤 又初→狂人（方案/正文） 主线 bus#13827 · 出站 bus#13841 ──────────── 【回 #13827｜接手确认 + 两问】 先认：渠道指标日报 ads_channel_metrics_daily_d、页面访问 dws_app_page_visit_d_d（B2）从现在起归你上生产；又初停手，不再改这两张 SQL / 编排 / S
- 2026-11-17 | 技术中台数据中心-开发小组 | 迦勒 | # 日报 · 迦勒·2026-11-17 [REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:2026-11-17] > 提交人: 迦勒 > 工号: DN4068 > 岗位: 后端 BE > 层级: L1 > 日期: 2026-11-17 ## 【今日结果】 - [TQ-002 | DMP系统] 生产 OpenMetad
