---
date: 2026-11-04
tags: [dim_user_snap, dim_device_snap, uid_code, device_code, sdk_init, 口径, bus12330]
severity: high
domain: ops
---

# 用户/设备维度一律按「基础表使用说明」：只读 snap、带分区、用字典号

## 背景

知秋已审，平台设计文档：`/library/guide-user-device-base-tables-usage`（doc id 83；raw=`guide-user-device-base-tables-usage`）。bus#12330 要求以后写 SQL 用到用户/设备维度一律按这份来。本地镜像：`~/.dc-platform/memory/guides/guide-user-device-base-tables-usage.md`。

## 坑 / 错误做法

- 读 `dim_user_all_d` / 视图 `dim_user_all_d_v`（作废待停更；视图永远指向最新一天）
- 只按 `uid` 去重/计数，不带 `app_id`
- 用非 sdk_init 事件里的设备号算设备规模
- 业务 SQL 自己算「真实渠道优先」
- bitmap 不用 `uid_code`/`device_code`，或拿号表 `dim_*_code_h` 去 join（号表只保留 30 天、只记发号过程）
- 报表读设备日间小时版当定稿

## 正确做法

1. **用户维度**：只读 `dim.dim_user_snap`，**必须** `snap_dt` 分区；天任务 `snap_dt=D`，小时/日间挂属性用 `snap_dt=D-1`（再叠当天日间表）
2. **用户唯一键**：`(app_id, uid)`
3. **设备只认 sdk_init**：规模/全表来自 `dim.dim_device_snap`；活跃读 `dwm.dwm_device_intraday_d_d`（对账以 D+1 07 点日结为准）
4. **渠道直接取**：用户日间/快照 `channel`；设备渠道取全表 `dim_device_snap.channel`（不要用日间表 channel 当设备渠道）
5. **bitmap**：用 `uid_code` / `device_code`，且必须与 `app_id` 一起；怪 uid 无号、不计入
6. 分区未就绪用 `assert_true` 校验，勿读错日或空分区硬算

## 验证

- 新 SQL / 改口径涉及用户或设备维时：对照平台文档五条硬规则自检
- 有疑问 bus 问狂人，勿自行改快照口径

## 关联

- bus#12330
- 平台：`/library/guide-user-device-base-tables-usage`
- 本地：`~/.dc-platform/memory/guides/guide-user-device-base-tables-usage.md`
