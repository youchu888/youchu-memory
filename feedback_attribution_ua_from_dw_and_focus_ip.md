---
name: attribution ua from dw and focus ip
description: For attribution analysis, user_agent must be sourced from dw.dw_user_event_detail; focus future root-cause analysis on UA parsing quality and IP reporting quality.
type: feedback
---
For channel attribution analysis, always take `user_agent` from `dw.dw_user_event_detail` rather than downstream DWD candidate-side fields, and prioritize two root-cause tracks: whether UA contains usable information that current parsing fails to extract, and whether the reported IP itself is wrong or unusable.

**Why:** The user explicitly corrected the analysis direction: the key questions are whether UA parsing is correct and whether IP reporting is problematic. They also required UA sampling from the raw DW source, not downstream derived tables.

**How to apply:** In future attribution investigations, fetch UA from `dw.dw_user_event_detail` with bounded `event_time`, compare current candidate-side extracted fields against information still present in raw UA strings, and quantify IP issues (empty/private/mismatched/shared-collision) before concluding that scoring logic is the main problem.
