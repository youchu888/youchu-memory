# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-07 · 最新归档：`sessions/tg-rotate-2026-09-07-2207.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- [LESSON: daily-report|TG 已推错误初稿时，以主人改定稿覆盖本地与云端，再 `post_daily_report_to_dm.py --force` 重推，勿在 upload 前改定稿正文]
- 日报自动初稿若只吃到部分 work-log（当日 ops-mirror / 旧 bus 噪音多），容易漏掉其它主题交付；2026-09-07 即漏了「归因升级」，只写了指标库两条。
- 交付面分散、流水不干净时，自动写稿比「交付集中、流水干净」的日期更容易漏任务；不能假设上周能扫全今天也能。
- 写稿来源须合并：双机 work-log、当日全部 agent transcript、派单 provenance（`task_provenance.jsonl` / agent-bus inbox），同一主题去重后再归纳，不能单靠单一流水。
- TG 定时推送（如 21:37）可能在主人改定前就发出**初稿**；明日动作也可能与定稿不一致（例：初稿写「大漏斗观察」，定稿是指标库审核后灌生产 + 归因测试发布）。
- 主人贴出的定稿是最终权威版本：本地 `.cursor/work-log/reports/日报-YYYY-MM-DD.md` 须**原封不动**覆盖，再上传云端。
- 「上传云端」与「推 TG」是两条链路：云端用 `upload_work_report.py --date YYYY-MM-DD`；TG 用 `post_daily_report_to_dm.py`；初稿推错后需 `--force` 重推定稿。
- 补救顺序：定稿落盘 → 上传云端（同日同类型会覆盖，记录 ID 可不变）→ TG `--force` 重推 → 私聊确认收到补全版。
- 自动稿漏任务时，优先查「哪些实活没进 work-log / 没被 transcript 扫到」，而不是改推送脚本本身。
- 日报结果条按真实交付写 1～3 条；当天有指标库 + 归因等多线并行时，每条对应一个可验收交付，避免只写最显眼的主题。
- 用户问「为什么失败」时，先对齐**失败对象**（日报上传 / 大漏斗 / 打卡 / TG 会话状态），不要默认某一种。
- 回报结论要带可核验字段：日期、云端 record ID、最终状态（inserted/updated），便于用户自助核对。
- [LESSON: daily-report,upload|同日重复上传云端是 updated 覆盖同一条记录，inserted→updated 属正常，勿误判为异常]
- 排查顺序：终端输出 → 相关任务日志（如 explain）→ 最近建表/跑数记录 → 再查对应 API/脚本结果。
- 日报「上传云端」成功判定：查 `upload_work_report.py` 执行结果；`code=0` 且有云端记录 ID 即成功。
- 同日同类型日报重复上传会走 **update 覆盖**（先 `inserted` 后 `updated` 是正常行为，不是失败）。
- 云端填报页看不到记录时，优先核对**日期筛选**（如 `2026-09-05`）和页面缓存，让用户刷新后再查。
- TG 里 agent 会话**变红/显示失败**，常与真实 API 结果脱钩；需单独核对实际上传/任务日志，不能只看 TG 状态。

