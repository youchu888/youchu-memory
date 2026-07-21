---
name: Quantify numeric errors and HLL tolerance
description: For every data validation, locate numeric discrepancy root cause; if metric uses HLL/approximation, estimate error rate and judge whether it is acceptable.
type: feedback
---
Always quantify numeric discrepancies in validation results and trace the cause instead of stopping at “basic pass”. If a metric is approximate (for example HLL-based), compute an explicit error rate and state whether it is within a reasonable tolerance range.

**Why:** The user requires all validation outcomes to explain residual numeric differences, and approximate algorithms must still be evaluated against acceptable error bounds.

**How to apply:** In every future datacheck/report, include (1) discrepancy decomposition, (2) root-cause attribution or pending evidence, and (3) error-rate assessment for HLL/approximate metrics with a clear pass/fail-or-risk judgment.