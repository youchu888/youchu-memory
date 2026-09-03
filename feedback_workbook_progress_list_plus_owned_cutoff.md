# Feedback：狂人 bus 任务清单问进度 → 清单主责 + 自开实责 · 统一查「截至汇报前」

**来源**：主人 2026-09-03 当面定口径（接「不要秒回」）

## 触发

狂人（worker_ant）通过 **agent-bus / 工作簿 / 群进展点名** 发来任务清单并问进度。

## 正确做法（三步，缺一不可）

1. **清单主责**：从狂人清单里抽出 **又初负责** 的项，逐项实查进度  
2. **自开实责**：加上我们**实际在负责**但不一定写在当日清单上的事（task 板自开 / `workbook_supplemental.json` / 当日已登簿大活）  
3. **统一口径**：两段合并后，全部按 **「截至汇报当前」**（工作簿日 D → cutoff=D-1）整理再回；**禁止秒回罐头**；当天新活留次日

## 禁止

- 清单到了立刻「行，我来」/ 精简秒回  
- 只回清单项、漏掉自开项（或反过来只回自开）  
- 日复一日同一套话、不带 T-1 探针 / work-log 近况  
- 把「今天刚干的」混进当天工作簿进展

## 落地

- 自动群进展：`workbook_progress_service.py`（单条实查）+ `group_workbook_progress_handler.py`（禁双条 follow-up）  
- bus 人工回复：同一套三步，先实查再 reply  
- 权威板：`project_youchu_workbook_tasks.md` + `workbook_supplemental.json`

## 关联

- `feedback_workbook_progress_cutoff_not_today.md`  
- `feedback_workbook_progress_confirm_before_group.md`  
- lesson：`2026-08-07-群工作簿进展须当日实查-新大活次日登簿.md`
