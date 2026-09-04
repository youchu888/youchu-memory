# 未结交接（MEMORY_OPEN）

> **体积目标 ≤3KB** · 每次冷启动全文注入 · **结了当场删行**  
> 全量索引仍见 [`MEMORY.md`](MEMORY.md) / [`lessons/_index.md`](lessons/_index.md)  
> 更新：2026-08-31

## 进行中

- [x] **大漏斗 sandbox**：已 push（`0de62fd0`/`9d29f0f5`）；等狂人与 uid_map 同链 PASS。
- [x] **指标库 Phase1 video 批**：已 apply，published 120；下一批 other 归类。

- [ ] **prod 海豚告警处置（old-mac 专责）**：主人 2026-09-01 确认**按狂人安排**——告警驱动处置（不另建夜间全量扫）；playbook=`playbook_server_monitor_incident.md`（bus#7708+#7742）；先 part_01；**确认事故→立刻修含改代码，修完再报**；日常非事故变更仍等知秋 GO。
- [x] **TG 问狂人标题修复（old-mac 应用）**：2026-09-01 old-mac 已 apply + restart（标题：超时→已转问狂人）。
- [x] **记忆系统 P0**：`PINNED.md` + `MEMORY_OPEN.md` + 瘦身 bootstrap（pinned/OPEN/recent-by-mtime）+ `memory_weekly_hygiene.sh`。存量索引/正文保留。
- [ ] **记忆系统 P1 养成**：每周跑 hygiene；新经验沉前查重；纠正≥2 次写入 PINNED。
- [ ] **设备标签指纹**：`bb905feb` 已交复审（#7830/#7831）；等 PASS 再沙箱 explain；dim/dwm/宽表 HOLD。
- [x] **页面访问 / 归因**：主人 2026-09-02 — **不盯卡点**（灰度/口径等产品线卡点挂起）；**分区巡检、日常扫链继续**；有安排再通知。
- [ ] **页面访问 DWS 对接**：`ops_system/04.dws/dws_app_page_visit_d_d/` 本地改动未要求则先别 commit。

## 待跟进

- 可回狂人一版差异说明（保留自动 bootstrap/playbook；补最近动过与周清理）。

## 退出条件

- P1：连续一周按 hygiene checklist 跑过且 OPEN 无已结残留 → 勾掉养成项。
- 页面访问：用户结案或改派后删行。

- [x] **大漏斗摘 new 表**：主人 2026-09-04「我们自己干」→ 已改 `stage_metrics` 全切 `*_r`（含 `dwd_sdk_init_d_r`）；legacy daily 冻结；待 push + 沙箱 explain
