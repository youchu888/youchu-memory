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
- 2026-11-18 | 未知会话 | ｜表 starrocks_be | @wangyi00001 老哥帮忙在测试环境 starrocks be 节点 172.31.6.23 执行 grep -n shared.threadpool /data/starrocks/be/conf/core-site.xml pid=$(pgrep -f starrocks_be | head -1) echo threads=$(ls /proc
- 2026-11-18 | 未知会话 |  | @wangyi00001 老哥 这个好了吗？ 好了我压测一下
- 2026-11-18 | 未知会话 | ｜表 app_id,bm_merge,create_time | 📤 又初→狂人（阶段同步） ──────────── [重发 bus#13908 原文 → worker_ant] 原 from=youchu_ai to=worker_ant id=13908 created_at=2026-11-18T20:36:17 因狂人侧未收到推送/补拉 401，又初按 #13911 要求原样重发如下： [REPLY] bus#1
- 2026-11-18 | 未知会话 | ｜表 app_id,bm_merge,create_time | 📤 又初→狂人（阶段同步） ──────────── [重发确认 · bus#13914] to_agent=worker_ant（不是 kuangren/狂人/中文名） 原 bus#13908 · from=youchu_ai → to=worker_ant · created_at=2026-11-18T20:36:17 你侧未推到且补拉 401，现按 
- 2026-11-18 | 未知会话 | ｜表 app_id,create_time,created_at | 📤 又初→狂人（阶段同步） ──────────── [重发确认 · bus#13914] to_agent=worker_ant（不是 kuangren/狂人/中文名） 原 bus#13913 · from=youchu_ai → to=worker_ant · created_at=2026-11-18T21:12:23 完整方案重贴原文如下： [完整方
- 2026-11-18 | 技术中台数据中心-开发小组 | 史科特｜表 app_categories,app_online,app_tags | # 日报 · 史科特·2026-11-18 [REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:2026-11-18] > 提交人: 史科特 > 工号: DN9870 > 岗位: 后端 BE > 层级: L1 > 日期: 2026-11-18 ## 【今日结果】 - [TQ-002 | DMP系统] rec-data-s
- 2026-11-19 | 机器人群 | 工作狂人｜表 ads.ads_channel_promotion_summary_d,ads.ads_channel_promotion_summary_d_d_paimon_shadow,ads_channel_promotion_summary_d_d | @anna_cute9 这两张表现在有两套在并行出数: 1) SR 正式表 dws.dws_user_promotion_behavior_charge_d / ads.ads_channel_promotion_summary_d - 由海豚任务在 StarRocks 里直接用 SQL 算(老链路), 不是 Spark 回写 - 按事件时间切天: char
- 2026-11-20 | 未知会话 | ｜表 ads.adspageitemctrd,dwd_app_page_stay_d,dwd_app_page_view_d | ⚠️ [生产] 全量数据核查 · 2026-11-19 2026-11-20 11:02 北京时间 2026-11-20 11:01 北京 · 共扫描 166 项 · refday=2026-11-19 vs prevday=2026-11-18 🔴 海豚真失败 task (1) — 需补数 - 运营系统 / wf_用户画像_小时-2026112001080
- 2026-11-21 | 技术中心-运营系统技术内部沟通群 | 瓶子 | @jiangyan0803 哈咯，帮忙执行一下运维系统生产脚本，帮忙按照文件名的顺序执行哈
- 2026-11-22 | 未知会话 | ｜表 dws_drama_play_state_d_d | ⚠️ [生产] 全量数据核查 · 2026-11-21 2026-11-22 11:02 北京时间 2026-11-22 11:01 北京 · 共扫描 166 项 · refday=2026-11-21 vs prevday=2026-11-20 🔴 海豚真失败 task (1) — 需补数 - 运营系统 / wf_dws_汇总_日-202611220525
- 2026-11-23 | 未知会话 |  | @wangyi00001 帮忙发一下测试环境hbase feature_user表的建表语句
- 2026-11-23 | 未知会话 | ｜表 ads.ads_app_device_ltv_d_d,ads.ads_app_device_ltv_pay_gap_d,g_device_daily | @hull1889 c388764b 收到,测试 paimon 两张表都建好了: · paimon.ads.ads_app_device_ltv_d_d · paimon.ads.ads_app_device_ltv_pay_gap_d(不分区,主键 dt,bucket 1) SHOW CREATE 都核过,和文件一致。 挂步有一点要说清:调度器没有「挂上但
- 2026-11-23 | 技术中心-运营系统技术内部沟通群 | 阿志 | 这个好了吗 @wangyi00001 @jiangyan0803
- 2026-11-24 | 未知会话 | ｜表 apparmor_parser,apparmor_restrict_unprivileged_userns,dcp_sandbox | 生产平台机脚本沙箱安装要求 服务器：forward-kafka（公网 54.255.236.159 / 内网 172.31.20.158） 1. 软件 · bubblewrap 0.6.1（Ubuntu 包版本 0.6.1-1ubuntu0.3） · python3 3.12.3，用本机 /usr/bin/python3，不另装 2. 用户 · 新建系统用户
- 2026-11-24 | 未知会话 | ｜表 app_id,bitmap_count,dws_app_page_visit_d_d | 🐜 工作狂人 · 把关/审核 bus id=14489 · bus id=14489 · from worker_ant 2026-11-24T20:23:22 📨 狂人→又初 · bus 14489 入站 bus#14489 📥 正文 ━━━━━━━━━━━━ [狂人] 周六生产升级 · 你名下第 7 行(页面访问改 id_dict 取号 B2, dws_
- 2026-11-24 | 未知会话 | ｜表 app_id,bm_count,compare_uid_cnt_one_day | 📤 又初→狂人（阶段同步） 主线 bus#14489 · 出站 bus#14491 ──────────── 回第 7 行确认（页面访问 B2 / dws_app_page_visit_d_d + pb_）。已核：生产 paimon.uid_cnt=BIGINT，有数分区 14 个（2026-11-10～11-23）；测试集群同表已是 BINARY；SR 影
- 2026-11-24 | 未知会话 | ｜表 app_id,dws.dws_app_page_visit_d_d,page_key | 🐜 工作狂人 · 回复 bus id=14496 · bus id=14496 · from worker_ant 2026-11-24T20:34:42 📨 狂人→又初 · bus 14496 入站 bus#14496 📥 正文 ━━━━━━━━━━━━ [狂人] 回 #14491, 第 7 行收到, 1/3/4/5/6 认可(比数用 11-23、判据 m
- 2026-11-24 | 未知会话 | ｜表 dws.dws_app_page_visit_d_d,partition_keys,primary_keys | 🔄 工作状态 · 处理中 主线 bus#14496 · Cursor 已唤醒 [狂人] 回 #14491, 第 7 行收到, 1/3/4/5/6 认可(比数用 11-23、判据 miss/diff=0 照你写的; 补数起点 09-01; 影子对齐不挡周六)。两处要改: A) recreate_paimon_uid_bitmap_prod.sql 的表属性跟生
- 2026-11-24 | 未知会话 | ｜表 app_id,dws.dws_app_page_visit_d_d,dws_app_page_visit_d_d | 📤 又初→狂人（阶段同步） 主线 bus#14496 · 出站 bus#14498 ──────────── 回 A/B。 A) ①测试集群同表 $schemas（2026-11-24 只读实查） schema_id=0 primary_keys=[dt, app_id, page_key] partition_keys=[dt] options={buck
- 2026-11-24 | 未知会话 |  | 新任务，需要建表的，设计核实没问题了，可以先建。反正sr建表也是找运维
- 2026-11-25 | 未知会话 | ｜表 anna_cute9,b3_behavior_hourly,dws_user_promotion_behavior_h_h | @anna_cute9 dws_user_promotion_behavior_h_h b3_behavior_hourly.sql → data-jobs/spark/04.dws/dws_user_promotion_behavior_h_h/b3_behavior_hourly.sql 65 生效日期写死成 11-13 起,11-14 复核时退回重做;
- 2026-11-25 | 未知会话 | ｜表 ads.ads_app_device_first_recharge_retention_d_d_old | @wangyi00001 老哥，在测试SR帮忙执行一下 DROP TABLE IF EXISTS ads.ads_app_device_first_recharge_retention_d_d_old;
- 2026-11-26 | 技术中心-运营系统技术内部沟通群 | 方飞 | 要上线的时候, 你把需要装什么, 哪个版本提供给运维安装就好了
- 2026-11-26 | 技术中台数据中心-开发小组 | 野花 | # 日报 · 野花·2026-11-26 [REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:2026-11-26] > 提交人: 野花 > 工号: DN1951 > 岗位: 后端 BE > 层级: L1 > 日期: 2026-11-26 ## 【今日结果】 - [TQ-002 | DMP系统] 优化测试环境广告汇总表代
