# Feedback：狂人 bus 任务清单问进度 → 清单主责 + 自开实责 · 统一查「截至汇报前」

**来源**：主人 2026-09-03 当面定口径（接「不要秒回」）；**2026-10-02 再强调禁模板**

## 触发

狂人（worker_ant）通过 **agent-bus / 工作簿 / 群进展点名** 发来任务清单并问进度。

## 正确做法（缺一不可）

1. **先实查再回**（主人 2026-10-02 / 2026-10-09）：正文以 cutoff 日日报【今日结果】原句为准，对应表再附探针数字。禁止「未查到探针 / 不套模板 / 任务板仅挂账」。本机 work-log 若只有空的「已完成」占位，继续读 memory 合并稿里的日报，匹配时保留方括号中的任务名。  
2. **清单主责**：从狂人清单里抽出 **又初负责** 的项，逐项挂上实证进度  
3. **自开实责**：加上实际在干的事——权威读 `project_youchu_workbook_tasks.md`「自开任务」，再并 `workbook_supplemental.json`；正文【簿内主责】+【自开实责】  
4. **统一口径**：全部按 **「截至汇报前」**（工作簿日 D → cutoff=D-1）；当天新活留次日；查不到就写「未查到实据」，不许用「进行中」糊弄  
5. **只 bus 回狂人**；不回群、不推「又初→群」私聊

## 禁止

- 清单到了立刻「行，我来」/ 精简秒回 / **任何未实查的模板段**  
- 只抄任务板状态（「进行中 · 【又初】」）当进展  
- 复读过期 supplemental note、日复一日同一套话  
- 只回清单项、漏掉自开项（或反过来只回自开）  
- 把「今天刚干的」混进当天工作簿进展  
- **群没收到原文却用 09:01 闹钟往群里发**  
- **bus 没收到清单就先回一版固定进度**

## 落地

- 自动**回群**：**已关**（Bot API 收不到狂人 bot；主人 2026-09-05 取消群回复）  
- **群簿仍要回**：Telethon 看见「今日工作簿」→ **force 实查** → **只 bus 给狂人**；无实证不成文  
- bus 入站清单：实查后 `reply`  
- 权威板：`project_youchu_workbook_tasks.md` + `workbook_supplemental.json`  
- 代码：`workbook_progress_service.py`（禁模板自检）+ `group_workbook_progress_handler.py`

## 关联

- `feedback_workbook_progress_cutoff_not_today.md`  
- `feedback_workbook_progress_confirm_before_group.md`  
- lesson：`2026-08-07-群工作簿进展须当日实查-新大活次日登簿.md`  
- lesson：`2026-10-02-holiday-skip-daily-report-workbook-bus-learn-0900.md`
