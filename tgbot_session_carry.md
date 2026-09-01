# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-01 · 最新归档：`sessions/tg-rotate-2026-09-01-2142.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 工作簿三件套须同频**：`project_youchu_workbook_tasks.md`（权威任务板）、`workbook_supplemental.json`（自开/增补项）、`.cursor/work-log/当日.md` 必须按**当天实活**一起更新；只写 work-log 不回写 task 板，群/bus 进展就会和 reality 脱节。
- PINNED #13 铁律**：读到 09:00 群工作簿或当天有新进展 → **当天内整表覆盖** `project_youchu_workbook_tasks.md`；大活自开也要登「自开任务」，不能只记 work-log。
- 11:00 后仍有交付**：不要只依赖 09:01 一次；应自动补发或私聊一句实态摘要，避免下午活漏报。
- 代码与配置须真读 JSON**：`workbook_progress_service.py` 里 `_local_tracking_items()` 若硬编码旧标题，即使 `workbook_supplemental.json` 已更新，群文案也不会变——增补项必须从 JSON 读。
- 进展汇报答问顺序**：先核对 task 板、work-log、各专项实态，再汇总；主人追问「为什么不执行」时先定位根因与落点文件，再补救，不复读模板。
- Spark/复审链状态表达**：代码本地已改但未 push、等狂人 PASS 前 dim/下游 **HOLD**——进展汇报须区分「写法层通过 / 远程未 push / 下游 HOLD」，避免写「已完成」。
- [LESSON: workbook|读到群簿或有大活交付后，当天同步 task 板 + supplemental + work-log，大活后再补发进展，禁止只依赖 09:01 一次]
- [LESSON: workbook|workbook_progress_service 增补项必须读 workbook_supplemental.json，禁止 _local_tracking_items 硬编码]
- **工作簿三件套须同频**：`project_youchu_workbook_tasks.md`（权威任务板）、`workbook_supplemental.json`（自开/增补项）、`.cursor/work-log/当日.md` 必须按**当天实活**一起更新；只写 work-log 不回写 task 板，群/bus 进展就会和 reality 脱节。
- **PINNED #13 铁律**：读到 09:00 群工作簿或当天有新进展 → **当天内整表覆盖** `project_youchu_workbook_tasks.md`；大活自开也要登「自开任务」，不能只记 work-log。
- **09:01 自动汇报 ≠ 全天闭环**：定时发送若早于当天实活（work-log 仍空、下午才 push），主人看到的仍是旧态；不能发完一次就停。
- **大活交付须触发二次同步**：push / 交审 / 批处理 / bus 口径变更等「大活」完成后，**当天**再改 task 板 + supplemental + work-log，并补发进展（`--force-repost` 或等价机制）。
- **11:00 后仍有交付**：不要只依赖 09:01 一次；应自动补发或私聊一句实态摘要，避免下午活漏报。
- **代码与配置须真读 JSON**：`workbook_progress_service.py` 里 `_local_tracking_items()` 若硬编码旧标题，即使 `workbook_supplemental.json` 已更新，群文案也不会变——增补项必须从 JSON 读。
- **task 板 stale 自检**：`project_youchu_workbook_tasks.md` 整表更新时间 vs 当日 work-log / 群簿对比；超过 1 天未 sync 即执行缺口，不是信息缺口。
- 沙箱 explain：**材料 push 完 → 交狂人 review → 收到 PASS 再跑**；未审过禁止先 SSH 试跑。
- 任务进入「等审/已交材料」后必须立刻取消后续定时进度推送**；只在有 PASS/打回或状态变更时主动通知，禁止 13/15/17/19 式刷屏。
- [LESSON: tg-progress|agent-bus-review|wait-state|任务已交审或进入等 PASS 状态时，立即取消所有定时进度提醒；仅在审结、打回或需拍板时再私聊通知]

