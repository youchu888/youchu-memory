# 记忆召回捷径（自动生成 · 速度用）

> 索引：`/Users/mac/.dc-platform/memory/recall_index.jsonl` · 重建：`python3 omdb/tgbot/memory_recall.py --rebuild`
> Agent：遇同类问题先 `memory_recall.search(问句)` 或读本文件关键词行。

| 关键词钩子 | 路径 | 一句话 |
|---|---|---|
| ## 09 12 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-09-12-改-etl-前须摘-prd-原句入-spec-spec-自写条件不能当需求依据-口径争议以-gi.md` | 2026-09-12-改-etl-前须摘-prd-原句入-spec-spec-自 |
| ## 09 12 2026 agent_session_rotate app_i | `~/.dc-platform/memory/lessons/2026-09-12-需求写沿用现有关联时-禁止新增-app_id-device_id-安装-join-并宣称沿用旧规.md` | 2026-09-12-需求写沿用现有关联时-禁止新增-app_id-device |
| ## .0 .1 0. 09 1. | `~/.dc-platform/memory/lessons/2026-09-12-升级稿含-is_run_sync-已废弃-与黑名单互斥-不得再提审或开跑-已发产-session.md` | 2026-09-12-升级稿含-is_run_sync-已废弃-与黑名单互斥-不 |
| app_id+device_id join prd spec 」时 不得 | `sessions/tg-rotate-2026-09-12-1601.md` | 需求写「**沿用现有关联、不调整关联字段和匹配优先级**」时，不得把新增的 `a |
| dws_register_attribution_result_d spark  | `sessions/tg-rotate-2026-09-12-1601.md` | 归因升级**结果表**（`dws_register_attribution_re |
| 1—— 2~t app_id channel ip join | `sessions/tg-rotate-2026-09-12-1601.md` | 落地页**候选匹配**仍是 **`app_id` + IP**、事件早于注册、≤ |
| app_install attribution_fla attribution_ | `sessions/tg-rotate-2026-09-12-1601.md` | **上一版入围不连 `app_install`**：仅 `is_run=1` + |
| ios natural organic self uid 不了 | `sessions/tg-rotate-2026-09-12-1601.md` | 注册侧前置筛选（与安装无关）：**iOS、自然渠道**（`organic`/`n |
| 册最 同窗 同窗多次安装取 多次 安装 安装时间窗 | `sessions/tg-rotate-2026-09-12-1601.md` | 安装时间窗：**注册前 7 天 ~ 注册后 1 小时**；同窗多次安装取**离注 |
| app_id attribution_fl attribution_flag d | `sessions/tg-rotate-2026-09-12-1601.md` | 注册↔安装配对键：**`app_id` + `device_id`**（两边非空 |
| id 」不 」不是表 一对 一归 一次 | `sessions/tg-rotate-2026-09-12-1601.md` | 「**同一归因链路**」不是表、也没有链路 ID；指一次注册能否与一次安装**配 |
| 001 20260907 20260911 bus dev is_run_syn | `sessions/tg-rotate-2026-09-12-1601.md` | 废弃 session 标准动作：先查待审状态 → **撤回发布申请**（如 `d |
| app_id+device_id join lesson 入围 关联 写沿 | `sessions/tg-rotate-2026-09-12-1601.md` | [LESSON: 归因入围/需求写沿用现有关联时，禁止新增 app_id+dev |
| 一条 上若 下线 不要 不要为停一条任务而下线整条日批 为停 | `sessions/tg-rotate-2026-09-12-1601.md` | 日批上若有补数在跑：**不要为停一条任务而下线整条日批**；先确认实例状态再处置 |
| is_run_sync v1.0.11 上线 不等 不等黑名单上线再谈 两条 | `sessions/tg-rotate-2026-09-12-1601.md` | 归因 **V1.0.11 升级稿**（含 `is_run_sync` 回写）与* |
| ## 09 12 2026 agent_session_rotate attri | `~/.dc-platform/memory/lessons/2026-09-12-is_run-attribution-frontend-口径.md` | 2026-09-12-is_run-attribution-frontend-口 |
| flag is_run 一套 与黑 两者 两者职责分离 | `sessions/tg-rotate-2026-09-12-1101.md` | 口径问答模板：`is_run` 管展示与黑名单；归因入围另有一套 flag，两者 |
| flag is_run 「前 「归 」→ 不到 | `sessions/tg-rotate-2026-09-12-1101.md` | 排查「前端看不到 / 列表缺失」→ 先查 `is_run`；排查「归因没算 /  |
| flag is_run 主要 主要是前端展示开关 入围 前端 | `sessions/tg-rotate-2026-09-12-1101.md` | 现网**归因计算入围**已不靠 `is_run`，看**双 flag**；`is |
| is_run sync 不会 会保 保留 单状 | `sessions/tg-rotate-2026-09-12-1101.md` | sync **不会**把已有 `is_run = 0` 的行改回 1；拉黑/黑名 |
| app is_run sync 会自 会自动写入 写入 | `sessions/tg-rotate-2026-09-12-1101.md` | 日批 sync 对**新入围 app** 会自动写入 `is_run = 1`。 |
| ifnull is_run null 主列 列表 前端 | `sessions/tg-rotate-2026-09-12-1101.md` | 前端主列表过滤条件：`IFNULL(is_run, 0) = 1`；NULL 视 |
| dim.dim_app_attribution_config.is_run 值先 | `sessions/tg-rotate-2026-09-12-1101.md` | `dim.dim_app_attribution_config.is_run`： |
| ho hot（须同时看「按时间最近动过」） ot t（ 「按 」） | `sessions/tg-rotate-2026-09-12-1101.md` | > **体积策略**：硬注入小而准；禁止只看 hot（须同时看「按时间最近动过」 |
| ## 09 11 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-09-11-页面浏览入围按用户日全局过闸-升维回写列齐再入库.md` | 2026-09-11-页面浏览入围按用户日全局过闸-升维回写列齐再入库 |
| ## 09 11 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-09-11-运行开关只做缺失配置补全-勿全量重刷覆盖已有配置.md` | 2026-09-11-运行开关只做缺失配置补全-勿全量重刷覆盖已有配置 |
| +「 +「已完成」 「已 专项 专项复盘 了什 | `sessions/tg-rotate-2026-09-11-2259.md` | 日报正文写法：任务名 + 做了什么 + 结果 +「已完成」；`【死锁阻碍】`/` |
| 1） op p1 to 与日 产发 | `sessions/tg-rotate-2026-09-11-2259.md` | 归因升级生产发布后的验收动作：核对近月数据与日批（TOP1） |
| 与全 交付 交审 付物 全量 册与 | `sessions/tg-rotate-2026-09-11-2259.md` | 归因升级交付物含后端对接总册与全量升级包，已提交审核 |
| 「只 为「 免全 全量 关改 升级 | `sessions/tg-rotate-2026-09-11-2259.md` | 归因升级运行开关改为「只补缺失配置」，避免全量覆盖已有配置 |
| 与无 候选 分分 分项 升级 因升 | `sessions/tg-rotate-2026-09-11-2259.md` | 归因升级：得分分项与无候选原因已在测试环境落地并验数通过 |
| 三项 两天 二列 二十 产侧 侧只 | `sessions/tg-rotate-2026-09-11-2259.md` | 归因看板二十二列版本：生产侧只读核对两天、十三项全过，并完成指标登记 |
| 侧完 入库 写列 列并 升维 回写 | `sessions/tg-rotate-2026-09-11-2259.md` | 大漏斗升维须补齐升维回写列并完成入库；测试表结构验收通过才算结构侧完成 |
| 「按 入围 全局 升维 口径 回「 | `sessions/tg-rotate-2026-09-11-2259.md` | 大漏斗升维：页面浏览入围口径改回「按用户日全局过闸」 |
| id inserted 上传 云端 云端记录 传成 | `sessions/tg-rotate-2026-09-11-2259.md` | 日报上传成功回执应带日期、云端记录 ID、状态（如 `inserted` 新建） |
| lesson 做缺 全量 关只 刷覆 勿全 | `sessions/tg-rotate-2026-09-11-2259.md` | [LESSON: 归因升级/运行开关只做缺失配置补全，勿全量重刷覆盖已有配置] |
| .cursor dd.md log mm reports work | `sessions/tg-rotate-2026-09-11-2259.md` | 用户贴定稿并说「按这个上传云端」时，以粘贴正文为准：先原样落盘到 `.curso |
| ## 09 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-09-10-主人贴定稿并说-上传云端-时-正文一字不改落盘再提交-同日上传为覆盖更新.md` | 2026-09-10-主人贴定稿并说-上传云端-时-正文一字不改落盘再提交-同日 |
| ## 09 10 2026 agent_session_rotate curso | `~/.dc-platform/memory/lessons/2026-09-10-prod-主键变更-重建表前-先确认补回责任方与天数-并核实下游已切读-未切读则重建前必须错峰协.md` | 2026-09-10-prod-主键变更-重建表前-先确认补回责任方与天数-并核 |
| 09 10 2026 prod v1.0.11 与生 | `sessions/tg-rotate-2026-09-10-2239.md` | 2026-09-10 续做项（周五截止）：事件漏斗改造与生产对齐、协助发布归因看 |
