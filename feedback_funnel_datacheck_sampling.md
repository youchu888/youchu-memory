---
name: funnel datacheck sampling
description: Prefer sampling over large full-table reconciliations for the channel funnel report; treat NULL/no-row and 0 as equivalent for sparse behavior metrics.
type: feedback
---
For `ads.ads_channel_daily_funnel_report_d`, default to sampling rather than large full-table reconciliations, and treat `NULL` / no-source-row and `0` as equivalent when validating sparse behavior metrics.

**Why:** Users in this funnel table naturally perform only some behaviors and not others, so broad full-table mismatch counts are noisy and misleading. The user explicitly said null represented as 0 is correct here and future checks should sample instead of scanning so much data.

**How to apply:** When validating this table in future sessions, run full checks only for structure/filter logic or after a very targeted code change. For metric-level reconciliation, prefer sampled apps/channels/segments and classify only non-NULL/0 value differences as hard mismatches.
