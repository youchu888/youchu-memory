# 未结交接（MEMORY_OPEN）

> **体积目标 ≤3KB** · 每次冷启动全文注入 · **结了当场删行**  
> 全量索引仍见 [`MEMORY.md`](MEMORY.md) / [`lessons/_index.md`](lessons/_index.md)  
> 更新：2026-10-28

## 进行中
- [ ] **bus#13228 海豚未迁全派出 / 已迁尽快切（又初 9 张）**：待迁 `ads_channel_summary_d`（禁读作废 retention）、dept/product 周月 bitmap×4、`ads_register_attribution_board/no_candidate`；影子修切 `dws_register_attribution_result_d`（6 列+rewrite 派生）/`dws_app_page_visit_d_d`（停留四列+uid_cnt 字典号 bitmap）。通用：runner、影子并行、字典号禁 hash64、全键 FULL JOIN 分类闭合、prod SR 轻量、用户维用 dim_user_snap。交付 SQL+step+影子DDL+首日核对，产编排狂人部署。进度：认领 ETA 已回；test 影子已 ALTER 6 列；`attr_rewrite_status.sql`+pushback 已落；prod SR 影子 35 列+rewrite 两列知秋已核（bus#13291）；prod SR 影子知秋已核；attr_rewrite COALESCE 坑已修 push `250e94c0`（bus#13297），待知秋复跑比对通过后挂 g_day_close_all。
- [ ] **bus#11677 改口径（废 #11627 历史补数）**：知秋 10-28 定——**test 不再追补历史**（不对就不对）；上线任务跟当前进度、有数即可。#11627「rerun 后补归因看板/无候选、渠道日指标、渠道汇总、部门周月/产品周」清单**作废**，不补 10-23 前。狂人：等设备补数+dim_user（dim_user 17:30 已完；设备今晚到 10-27）→ 只了结旧挂账格、不补中间空档 → 回执哪些线出当天数；**又初届时按当天分区查**，禁催历史补数/第二份 rerun。lesson=`2026-10-28-test不再追补历史-废11627补数清单-bus11677.md`。

- [ ] **bus#11621 定案（挂载仍有效）**：test spark_migrate 又初 S4 五步自挂；禁手改 full_chain/prod；渠道周月不挂；Paimon DDL 建前发狂人核。**历史水位追平/补 10-22 前已废**（见 #11677）；查数改等狂人报「当天有数」后按当天分区。lesson=`2026-10-27-S4测试五步自挂-禁手改full_chain-补数日不晚于追平水位.md`。
- [ ] **测试调度日常维护（知秋 11-10 / bus#13107）**：又初维护；狂人改系统。`keepRunning=true`（失败3/FATAL→SKIPPED；槽位120min未就绪不等；挂账>24h→SKIPPED）+ `sqlTextOverride`（user/device snap 断链读最近分区）。一夜复查通过(11-11 08:30)：小时跟到08、`11-11#00`日结05:43。日志=`/home/ec2-user/pipeline-runner/logs/fullchain_daemon_20261110_115207.log`。系统 bug 找狂人。lesson=`2026-11-11-bus13107-测试调度keepRunning一夜复查通过-日常维护归又初.md`。
- [ ] **归因 result 影子切正式（bus#10921/#10922/#10936）**：计划认可；**D1=10-21 起每天日结**经 bus 发狂人；剧本 `ops_system/00.pipeline/recon/recon_register_attribution_result_shadow_vs_formal.sql`；7 天对平后报切停海豚 `174729603403591`；配置类差先报。另：压测 wf `wf_dws_归因_paimon_shadow_日` 的 `result_d_r` 已按知秋定停（bus#11232，`flag=NO`）；同 wf apply/metrics 仍开，是否同停等知秋。

- [ ] **dim_channel_info_all_snap**：JDBC/SR 换源已停手（#11164）。**现网 SQL 以 `3ce1c124` 的 `dim_channel_info_all_sync.sql` md5 `68ebf206`（00 槽日快照）为准**（#11175）；勿再推 `230fa1fb`。**prod SR `dim.dim_channel_info_all`=0、prod snap 无分区**（#11251 复核）；卡业务后台写产。BitmapUdf 中间态以 Kryo 为准。
- [ ] **渠道日指标 013 + 管理报表 Spark 三表（bus#13074 HOLD）**：`ads_channel_metrics_daily_d`（`dev-20261016-013`）**先不迁、不推进、不再发布**（知秋 10-30：等 bitmap 字典后整体重做）。野花 S7 误发产后，11-09 补数 Kryo bitmap OOM；狂人 16:38 已撤产编排 `g_ads_channel_metrics_daily_d` 组+两步，**paimon/SR 影子表保留**。依赖它的 `dev-20261022-001/002/003`（稿 `ad004aed`）**一并等待**。lesson=`2026-11-10-bus13074-渠道日指标013停迁-产编排已撤.md`。
- [ ] **大漏斗优化停**。缓存 85 分钟、先按人聚合 75 分钟，都比基线 66 分钟慢。单扫试验 A 已取消（INSERT 未完成提交）。集群 SQL 已收回最初版。test SR 基线未覆盖。沙箱 Paimon 仍是试验 B 的数，要回到最初版需重跑，未开。（**注**：事件漏斗最新口径已发产、验收、补数完成；此项仅指性能试验，勿写成「漏斗未上线」。）
- [ ] **指标库（先 test 后 prod）**：隧道已通。`ubuntu@43.213.80.248` → MySQL `13306`、平台 `18012`。test 真库 published **658**；API `metric-library/concepts` 200。入口 `http://127.0.0.1:18012`；凭证 `~/.dc-platform/config/test-platform.env`；`ensure-test-platform-tunnels.sh`。**待**：MCP/`metric__search` 改指 test + 切读 concept（现仍打 standards）。prod HOLD。
- [ ] **设备标签 uid_map 指纹**：#8179 PASS；沙箱真跑 DONE（约 1.43 亿）；dim/宽表链仍 HOLD，勿并 full_chain。
- [ ] **prod 海豚告警处置（new-mac 专责）**：2026-09-27 自动化已迁 new-mac；playbook=`playbook_server_monitor_incident.md`；确认事故→立刻修含改代码。
- [ ] **记忆系统 P1 养成**：日清 22:50 已挂（`memory-daily-light-tidy`）；周 hygiene；沉前查重；纠正≥2 次写 PINNED。卡=`MEMORY_LIGHT.md`。
- [ ] **页面访问 DWS 对接**：`ops_system/04.dws/dws_app_page_visit_d_d/` 本地改动未要求则先别 commit。

## 已结（勿再当未完写进自评/日报）

- **自动化迁 new-mac（2026-09-28）**：memory sync 22:30 一次；狂人学习 22:40；flush 挂起；绿点跟 OneHR 打卡（离线≤15min）；群工作簿进展关。权威机 new-mac。
- **归因升级**：最新口径已发产、验收完成、本月数据已补全；日常分区巡检即可。
- **事件漏斗（大漏斗）**：最新口径已发产、验收完成、本月数据已补全（含 `funnel_backfill` 09-01～09-20）；日常日批维护即可。
- **页面访问 / 归因日常**：不盯产品卡点；分区巡检、扫链继续。

## 待跟进

- 可回狂人一版差异说明（保留自动 bootstrap/playbook；补最近动过与周清理）。

## 退出条件

- P1：连续一周按 hygiene checklist 跑过且 OPEN 无已结残留 → 勾掉养成项。
- 页面访问对接：用户结案或改派后删行。
- 管理报表 Spark 三表 / 013：等 bitmap 字典整体重做后再动（见 bus#13074）。
