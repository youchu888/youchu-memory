---
name: _h 表废弃，统一走 _d + hourly/daily 双链路
description: dwd_user_register_h/app_page_view_h/order_paid_h_v2 与 dim_user_h 已作废；用户快照统一走 dim_user_all。
type: project
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
2026-04-15 起，以下表在项目元数据中标记为"作废"：

- `dwd.dwd_user_register_h` → 由 `dwd.dwd_user_register_d_v2` 提供（DDL+hourly+daily 三件套）
- `dwd.dwd_app_page_view_h` → 由 `dwd.dwd_app_page_view_d` 提供（同上）
- `dwd.dwd_order_paid_h_v2` → 由 `dwd.dwd_order_paid_d` 提供（同上）
- `dim.dim_user_h` → 用户快照统一由 `dim.dim_user_all` 提供（hourly upsert + daily 收盘重算 T-1）

**Why:** DWD 小时表和日表重复维护、下游混用；小时快照的用户 dim 粒度设计过细导致 channel 不一致与跨 slot 冗余。统一到 _d + 新增 hourly 增量 + daily 收盘的模式，简化链路同时保留小时时效。

**How to apply:**
- 任何对这 4 张表的引用都要迁移到新目标表
- 查询 / 报告 / 核查 / playbook 出现这些作废表名时，优先推新目标表
- 物理 DROP 暂未执行；线上表仍可访问，但不会再有新数据写入
- 元数据权威来源：`.claude/database/metadata/program_mappings.md` 和 `project_metadata.md`（状态字段 "作废"）
- 视频事件链路例外：`dwd_video_event_h` 继续上线使用；`dwd_video_event_d` **已作废**（数据量大必须按小时分区）
