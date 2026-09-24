# 未结交接（MEMORY_OPEN）

> **体积目标 ≤3KB** · 每次冷启动全文注入 · **结了当场删行**  
> 全量索引仍见 [`MEMORY.md`](MEMORY.md) / [`lessons/_index.md`](lessons/_index.md)  
> 更新：2026-09-23

## 进行中

- [ ] **渠道报表周/月表**：DDL 已落仓 `ops_system/05.ads/ads_channel_promotion_summary_{w,m}/`；粒度自然周/月 × app × channel（不与日表简单加总）；**test 建表待 VPN**；ETL/口径未写。
- [ ] **大漏斗优化停**。缓存 85 分钟、先按人聚合 75 分钟，都比基线 66 分钟慢。单扫试验 A 已取消（INSERT 未完成提交）。集群 SQL 已收回最初版。test SR 基线未覆盖。沙箱 Paimon 仍是试验 B 的数，要回到最初版需重跑，未开。（**注**：事件漏斗最新口径已发产、验收、补数完成；此项仅指性能试验，勿写成「漏斗未上线」。）
- [ ] **指标库上线（主人定稿 B′）**：Phase2 ✅；D5 ✅；prod 同步包已出；**#8181 已转知秋，待确认后上线（灌产/切读 HOLD）**。**#8066 撞车点 diff 已回**（`COLLISION_DIFF.md`；entity/role=`INSERT IGNORE`）。界面跟单一入口，勿在旧三菜单上加东西。
- [ ] **设备标签 uid_map 指纹**：#8179 PASS；沙箱真跑 DONE（约 1.43 亿）；dim/宽表链仍 HOLD，勿并 full_chain。
- [ ] **prod 海豚告警处置（old-mac 专责）**：按狂人安排告警驱动；playbook=`playbook_server_monitor_incident.md`；确认事故→立刻修含改代码。
- [ ] **记忆系统 P1 养成**：每周 hygiene；沉前查重；纠正≥2 次写 PINNED。
- [ ] **页面访问 DWS 对接**：`ops_system/04.dws/dws_app_page_visit_d_d/` 本地改动未要求则先别 commit。

## 已结（勿再当未完写进自评/日报）

- **归因升级**：最新口径已发产、验收完成、本月数据已补全；日常分区巡检即可。
- **事件漏斗（大漏斗）**：最新口径已发产、验收完成、本月数据已补全（含 `funnel_backfill` 09-01～09-20）；日常日批维护即可。
- **页面访问 / 归因日常**：不盯产品卡点；分区巡检、扫链继续。

## 待跟进

- 可回狂人一版差异说明（保留自动 bootstrap/playbook；补最近动过与周清理）。

## 退出条件

- P1：连续一周按 hygiene checklist 跑过且 OPEN 无已结残留 → 勾掉养成项。
- 页面访问对接：用户结案或改派后删行。
