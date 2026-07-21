---
name: Lightweight DW event-detail validation first
description: For dw.dw_user_event_detail checks, first reconcile by event_id counts with date/app/channel dimensions; only drill into detailed rows for mismatches.
type: feedback
---
For `dw.dw_user_event_detail`, avoid heavy full-detail reconciliation queries by default.

**Why:** The table is very large, and broad deep scans can overload the database.

**How to apply:** First validate using lightweight checks (event_id-level reconciliation by date/app/channel and related aggregates). Only when mismatches are found, sample by `event_id` and then inspect detailed rows for root cause.