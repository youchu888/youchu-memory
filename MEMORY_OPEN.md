# 未结交接（MEMORY_OPEN）

> **体积目标 ≤3KB** · 每次冷启动全文注入 · **结了当场删行**  
> 全量索引仍见 [`MEMORY.md`](MEMORY.md) / [`lessons/_index.md`](lessons/_index.md)  
> 更新：2026-08-11

## 进行中

- [x] **记忆系统 P0**：`PINNED.md` + `MEMORY_OPEN.md` + 瘦身 bootstrap（pinned/OPEN/recent-by-mtime）+ `memory_weekly_hygiene.sh`。存量索引/正文保留。
- [ ] **记忆系统 P1 养成**：每周跑 hygiene；新经验沉前查重；纠正≥2 次写入 PINNED。
- [ ] **页面访问 DWS 对接**：`ops_system/04.dws/dws_app_page_visit_d_d/` 本地改动未要求则先别 commit。

## 待跟进

- 可回狂人一版差异说明（保留自动 bootstrap/playbook；补最近动过与周清理）。

## 退出条件

- P1：连续一周按 hygiene checklist 跑过且 OPEN 无已结残留 → 勾掉养成项。
- 页面访问：用户结案或改派后删行。
