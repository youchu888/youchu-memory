# TG 会话热携带（轮换沉淀 · 自动维护）

> 更新：2026-09-03 · 最新归档：`sessions/tg-rotate-2026-09-03-0615.md`
> 用途：Cursor resume 清空后，新会话仍能继承关键铁律/结论。

## 携带要点

- 「换了 VPN 重新推」标准动作：先 `git status` / 对比 `origin/dev`，再 `git push`；已对齐则如实报 Everything up-to-date，勿空推
- 沙箱 explain 统一走 `run_test.sh`，禁止用 `run_step_once.sh`（bus#7836 已明确）
- uid_map 沙箱 PASS 门槛：daily SQL 内嵌 `CREATE DATABASE/TABLE IF NOT EXISTS` + `${OUT_DB}`；建表 9 列与最终 SELECT 9 列逐项对齐（含 `first/last_uid_dt` 的 CAST 类型）
- 复审派单（bus#7838）闭环：60 秒内 ACK → 改完 push → reply 带 commit（如 `9d29f0f5`）与改动摘要；uid_map PASS 后等大漏斗复审再放行 explain
- 上传成功应回传：日期、云端记录 ID、首次状态（inserted）；主人追问「没上传吗」时先查同 ID 是否仍在（可能已是 updated），勿重复上传
- [LESSON: sandbox-explain|沙箱 explain 必须用 run_test.sh，禁止 run_step_once.sh]
- VPN 切换后 Cursor 会话 resume 可能失败；提示用户重发指令或发「重启 agent」强制新开，重启后应接上上一轮未完成的上下文继续干
- 大漏斗沙箱打回三类修法：`params.render` 补 `app_filter_e/v/n/c`（默认空串=全 app）；新增 `sandbox_steps_full.json`（`slots 00~23` 写全，`slot00`=`[metric_stg_d → d_d]`）；`stage_metrics`/`stage_wide` 两阶段 SQL 内嵌建表（对齐 uid_map 做法）
- 日报上传云端仅在主人明说「上传云端」时执行；稿源用 memory 定稿 `work-log/reports/日报-YYYY-MM-DD.md`，原样上传不改字
- 填报页查不到时优先提示按日期筛选/刷新缓存，而非假定上传失败
- > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」）。
- 日报定稿后**默认只推 TG**，**不会自动上传云端**；云端上传须主人明确说「上传云端」
- 核对「是否已上传云端」：查当日 work-log 有无 `upload_work_report.py` 执行记录，**不能**因 TG 已推就推断云端已传
- TG 是否已推：查 `.daily_report_dm_posted.json`（含推送时间戳）
- 定稿稿源：`~/.dc-platform/memory/work-log/reports/日报-YYYY-MM-DD.md`；本地镜像 `.cursor/work-log/reports/日报-YYYY-MM-DD.md`
- 历史日报可补传：定稿仍在则跑 `python3 .cursor/scripts/upload_work_report.py --date YYYY-MM-DD`，**原稿原样**上传，上传前不改字
- 补传成功回执应含：日期、云端 record ID、状态（如 `inserted`）；让用户在填报页按日期核对
- 主人问「昨天日报有没有上传云端」→ 先核三件套：**定稿是否存在 / TG 是否已推 / 云端是否已传**，分项回报

