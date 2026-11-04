---
name: feedback_user_device_base_tables_usage_guide
description: 写用户/设备维 SQL 前必读平台基础表使用说明
type: feedback
importance: high
triggers: dim_user dim_user_snap 设备 用户维度 uid_code device_code sdk_init 渠道
---

# 用户与设备基础表使用说明（知秋已审）

**以后怎么做**：凡 SQL 用到用户或设备维度，先读平台文档 `/library/guide-user-device-base-tables-usage`（bus#12330）。硬规则：只读 `dim_user_snap`+`snap_dt`；唯一键 `(app_id,uid)`；设备只认 sdk_init；渠道不重算；bitmap 用 `uid_code`/`device_code`。

**禁止**：`dim_user_all_d` / `dim_user_all_d_v`；只按 uid；自算真实渠道；拿号表 join 当全量字典。

出处：狂人起草 · 知秋 2026-11-04 审 · bus#12330  
lesson：`2026-11-04-用户设备基础表只读dim_user_snap须带snap_dt-bus12330.md`
