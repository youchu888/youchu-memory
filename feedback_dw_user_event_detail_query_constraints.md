---
name: dw user event detail query constraints
description: For this project, queries against dw.dw_user_event_detail must always include event_time limits and can be executed silently without asking first.
type: feedback
---
When querying `dw.dw_user_event_detail`, always add an `event_time` range filter and prefer day-by-day queries instead of full-table scans.

**Why:** The table is very large; unrestricted scans are too expensive and the user explicitly asked to avoid them.

**How to apply:** For attribution debugging or any other analysis that touches `dw.dw_user_event_detail`, add explicit time bounds in SQL and avoid whole-table queries. Also, execute SQL checks silently without asking for confirmation first unless the action is risky beyond normal querying.
