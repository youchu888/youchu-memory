# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-04 · 最新归档：`sessions/tg-rotate-2026-09-04-0647.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 主人问「日报怎么不发了」时，先区分是 **TG 没推** 还是 **云端没传**，再对症查；勿把私聊补传云端当成 TG 推送已恢复
- 主人私聊贴定稿正文并说「上传云端」→ **原封不动**落盘到 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`，再上传；上传前禁止改字
- 私聊补传场景：TG 定时未触发时，主人可直接贴已定稿日报走云端上传；两条线可并行缺失、分别补救
- `apply_tgbot_workbook_no_instant_ack.sh` 用于 tgbot workbook「禁即时 ack」类配置变更；与日报推送无直接耦合，别混为一谈
- 日报有**两条独立链路**：TG 私聊自动推送（old-mac 定时 `post_daily_report_to_dm.py`）与「上传云端」（主人指令后跑 `upload_work_report.py`）；一条没触发不代表另一条也停
- 云端上传成功回执应带：**日期、记录 ID、insert/update 状态、本地稿路径**；对话里一句确认即可，不必再贴全文
- TG 自动推送依赖 old-mac 定时链路（`prepare_daily_report_sync` → 写稿 → `post_daily_report_to_dm.py`）；new-mac 默认 skip TG 推送
- 日报正文写法仍按定稿模板：`【今日结果】` 业务向 1～3 条、`【死锁阻碍】`/`【专项复盘】` 默认留空、`【明日动作】` 带截止
- 上传云端 API 同日同类型会覆盖；本次 2026-09-03 为 `inserted`（新建），记录 ID 示例 `88066`
- 「换了 VPN 重新推」标准动作：先 `git status` / 对比 `origin/dev`，再 `git push`；已对齐则如实报 Everything up-to-date，勿空推
- 沙箱 explain 统一走 `run_test.sh`，禁止用 `run_step_once.sh`（bus#7836 已明确）
- uid_map 沙箱 PASS 门槛：daily SQL 内嵌 `CREATE DATABASE/TABLE IF NOT EXISTS` + `${OUT_DB}`；建表 9 列与最终 SELECT 9 列逐项对齐（含 `first/last_uid_dt` 的 CAST 类型）
- 复审派单（bus#7838）闭环：60 秒内 ACK → 改完 push → reply 带 commit（如 `9d29f0f5`）与改动摘要；uid_map PASS 后等大漏斗复审再放行 explain
- 上传成功应回传：日期、云端记录 ID、首次状态（inserted）；主人追问「没上传吗」时先查同 ID 是否仍在（可能已是 updated），勿重复上传
- [LESSON: sandbox-explain|沙箱 explain 必须用 run_test.sh，禁止 run_step_once.sh]
- VPN 切换后 Cursor 会话 resume 可能失败；提示用户重发指令或发「重启 agent」强制新开，重启后应接上上一轮未完成的上下文继续干
- 大漏斗沙箱打回三类修法：`params.render` 补 `app_filter_e/v/n/c`（默认空串=全 app）；新增 `sandbox_steps_full.json`（`slots 00~23` 写全，`slot00`=`[metric_stg_d → d_d]`）；`stage_metrics`/`stage_wide` 两阶段 SQL 内嵌建表（对齐 uid_map 做法）
- 日报上传云端仅在主人明说「上传云端」时执行；稿源用 memory 定稿 `work-log/reports/日报-YYYY-MM-DD.md`，原样上传不改字

