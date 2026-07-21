---
name: dwd_landing_page_click 不属于本项目
description: dwd_landing_page_click 不是 dc-parent 项目的表，统计/核查时排除
type: feedback
originSessionId: ce0993a6-f017-4276-92db-80fdc4888c85
---
`dwd.dwd_landing_page_click`（无 `_d` 后缀的旧表）不属于本项目，以后不用统计。

**Why:** 用户明确指出这个表不是本项目用的。

**How to apply:** 列 DWD 表清单、做数据核查、统计表数量时，排除 `dwd_landing_page_click`。本项目的落地页点击表是 `dwd_landing_page_click_d`。
