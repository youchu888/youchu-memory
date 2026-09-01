# 工作簿进展：报「截至汇报前」而非「当天实活」

## Why

主人 2026-09-01 明确：工作簿每天整理的是**又初负责模块、截止到汇报之前**的累计进度；**当天实活留到次日工作簿再报**。把下午 Spark/指标库进展塞进当天 09:01 或 force-repost，属于口径错误。

## How to apply

1. **汇报日 D 的 09:01 群进展** = 各模块状态 **截至 D-1**（cutoff），不含 D 当天交付。
2. **D 当天实活** → 写 `.cursor/work-log/D.md` + task 板「当日实活」区；**D+1 工作簿**再报。
3. `workbook_progress_service.py`：work-log 叙事只读 `_report_cutoff_date(D)`，正文标「口径：截至 {cutoff}」。
4. **禁止**因大活交付在同日 force-repost 工作簿（除非主人明确要求补发）。
5. 私聊问「今天进展」可报当日；**工作簿/群进展**走 cutoff 规则。
