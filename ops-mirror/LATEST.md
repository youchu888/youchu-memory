# ops-mirror · LATEST（权威机 `old-mac`）
> 更新: 2026-11-24 22:45:55 +0800

详见当日: `ops-mirror/hosts/old-mac/2026-11-24.md`

## 未结案 agent-bus

（无未结案 bus）

## 近期任务溯源（摘录）

| 时间 | 标签 | 来源 | 状态 | 摘要 |
|---|---|---|---|---|
| 2026-11-23 10:01 | 私聊#635 | telegram_dm | dispatched | 什么时候打卡呢 |
| 2026-11-23 15:21 | 群派单#380 | worker_ant_group | completed | @hull1889 测试 paimon 按你 06300d1a 的建表文件建了: 1) paimon.ads.ads_app_device_ltv_d_d 已建 |
| 2026-11-23 15:32 | 群派单#381 | worker_ant_group | completed | @hull1889 c388764b 收到,测试 paimon 两张表都建好了: · paimon.ads.ads_app_device_ltv_d_d · p |
| 2026-11-23 15:59 | 群派单#382 | worker_ant_group | completed | @hull1889 bus#14384 收到,正在挂:测试编排 g_device_daily 03 槽,计算步排 device_order_paid_v3_da |
| 2026-11-23 17:00 | 群派单#383 | worker_ant_group | completed | @hull1889 设备 LTV 已挂测试:测试编排 v40,北京 11-23 17 点槽起生效。g_device_daily 里 device_order_p |
| 2026-11-23 17:22 | 私聊#636 | telegram_dm | dispatched | 我感觉你现在没有之前好用了，可以恢复到之前的状态吗？任务发给你现在都看不见回复的 |
| 2026-11-23 18:17 | 私聊#637 | telegram_dm | completed | 每日学习不是让你取消了吗？为什么还每天发呢 |
| 2026-11-23 18:20 | 私聊#638 | telegram_dm | completed | 细节已发 bus 给初儿(#14392)。 狂人说发了bus，查一下有收到吗 |
| 2026-11-23 18:25 | 私聊#639 | telegram_dm | completed | 没有同步消息到机器人里，我也没看到，是什么原因 |
| 2026-11-23 21:22 | 群派单#384 | worker_ant_group | completed | bus#14417 收到。我先按规范审一遍建表稿，审过就走测试平台的建表接口，在测试集群建 ads_app_device_first_recharge_rete |
| 2026-11-23 21:25 | 群派单#385 | worker_ant_group | completed | 更正 bus#14417：这张表我不单独建，测试也不建。知秋定了：建表跟着任务走，请在开发平台的会话 dev-20261123-001 里按流程推进，表随任务一 |
| 2026-11-23 22:13 | 群派单#386 | worker_ant_group | completed | bus#14419 已回（#14420）。dev-20261123-001 在平台上记的是 Spark 任务，插件代码也是按这个打开 Spark 面板，这块没问 |
| 2026-11-23 22:21 | 群派单#387 | worker_ant_group | completed | 更正：1.0.30 正式版现在还不能发。生产平台现网是 1.1.0，发布的插件是 1.0.13。1.0.30 要等周五（11-27）生产平台升到 2.8.4 之 |
| 2026-11-23 22:42 | 群派单#388 | worker_ant_group | completed | 对，1.0.13 没有“上传并部署”。这一步是 1.0.30 加上平台 2.8.4 才有的新流程，生产要到周五（11-27）升级后才能用。 1.0.13 的 S |
| 2026-11-24 16:30 | 群派单#389 | worker_ant_group | completed | 还没改。第 2 点要等日结拆分上生产，现在生产还是旧编排：dwsuserpromotionbehaviorhh 既在 gsettlebehavior 入口，又在 |
| 2026-11-24 16:41 | 群派单#390 | worker_ant_group | completed | 好，已记下。日结拆分上生产后我在群里 @你。 |
| 2026-11-24 21:45 | 私聊#640 | telegram_dm | completed | ## 【今日结果】 - [TQ-002 | DMP系统] 页面访问：按周六生产升级确认，补齐生产湖表人数位图建表与删表重建脚本，明确类型须重建并回执周三比一天与 |
| 2026-11-24 21:59 | 群派单#391 | worker_ant_group | completed | @mati18899 #14502 来源分析 PRD r50 已审完，意见 11 条已发欧阳克（bus#14505）。建议先改的四条： 1. 留存表和 LTV  |
