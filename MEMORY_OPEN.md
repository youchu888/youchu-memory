# 未结交接（MEMORY_OPEN）

> **体积目标 ≤3KB** · 每次冷启动全文注入 · **结了当场删行**  
> 全量索引仍见 [`MEMORY.md`](MEMORY.md) / [`lessons/_index.md`](lessons/_index.md)  
> 更新：2026-09-12

## 进行中

- [ ] **大漏斗再试两刀** dt=2026-09-11。生产链有这步但无已完成耗时。试验B（先按人收口再挂属性）已开跑，日志 `/tmp/funnel_exp_b_20260911.log`。试验A（每表只扫一遍）排队。基线仍是 test SR 66 分钟那版，未覆盖。本地 SQL 已回到优化前口径。
- [ ] **指标库上线（主人定稿 B′）**：Phase2 ✅；D5 ✅；prod 同步包已出；**#8181 已转知秋，GO 前灌产/切读 HOLD**。**#8066 撞车点 diff 已回**（`COLLISION_DIFF.md`；entity/role=`INSERT IGNORE`）。界面跟单一入口，勿在旧三菜单上加东西。
- [ ] **设备标签 uid_map 指纹**：#8179 PASS；**沙箱 explain PASS**（hadoop-1 `/tmp/uid_map_explain_20260907.log`）；sqlFile 须绝对路径；下一步真跑三规模数；不动 full_chain。
- [ ] **prod 海豚告警处置（old-mac 专责）**：按狂人安排告警驱动；playbook=`playbook_server_monitor_incident.md`；确认事故→立刻修含改代码。
- [ ] **记忆系统 P1 养成**：每周 hygiene；沉前查重；纠正≥2 次写 PINNED。
- [x] **页面访问 / 归因**：主人 2026-09-02 — **不盯卡点**；分区巡检、日常扫链继续。
- [ ] **页面访问 DWS 对接**：`ops_system/04.dws/dws_app_page_visit_d_d/` 本地改动未要求则先别 commit。

## 待跟进

- 可回狂人一版差异说明（保留自动 bootstrap/playbook；补最近动过与周清理）。

## 退出条件

- P1：连续一周按 hygiene checklist 跑过且 OPEN 无已结残留 → 勾掉养成项。
- 页面访问：用户结案或改派后删行。

- [x] **大漏斗摘 new 表**：`563013e7`/`8b613fb6` 已 push；集群 SQL 已同步；**沙箱 explain 已起**（SF-81 · dt=2026-09-04 · `/tmp/funnel_explain_20260904.log`）；explain 过→真跑出数
