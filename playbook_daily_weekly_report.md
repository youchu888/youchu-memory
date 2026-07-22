# Playbook：日报 / 周报（基于 work-log）

> 维护人：又初 · 本地 playbook · 不进 Git  
> 日历：[`reference_work_calendar_cn.md`](reference_work_calendar_cn.md)

## 触发

| 类型 | 触发 |
|------|------|
| 日报 | 用户说「日报/今日总结」；或 **工作日** 21:30 Asia/Shanghai 自动 |
| 周报 | 用户说「周报/上周总结/本周计划」 |

## 日历规则（摘要）

| 项 | 规则 |
|----|------|
| 周报统计周期 | **自然周**（周一 00:00 ~ 周日 24:00），`YYYY-Www` |
| 常规工作日 | **周一至周六**（6 天） |
| 常规休息 | 周日 |
| 法定假日 | 国务院安排，**不要求日报**，不计入「应完成工作日」 |
| 调休上班 | 国务院指定日（含部分周日），**计工作日**，需日报 |

## 数据源（按优先级）

**日报内容只来自当日用户提问/交办**，不臆造未交办项。

1. **当日** `agent-transcripts/**/*.jsonl` 中 `"role":"user"` 消息（主来源）
2. 当日对话上下文中的完成结果
3. **`work-log/YYYY-MM-DD.md`**（若已有，用于核对）
4. `git log --since=<当日0点> --until=<次日0点>`（辅助）
5. `lessons/_index.md`（仅写【死锁阻碍】）

## 双 Mac 统一汇总（2026-07-22）

写日报前**必须**先合并两机流水，禁止只根据当前 Cursor 会话：

```bash
python3 ~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py
# 或直接：
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

| 读什么 | 路径 |
|--------|------|
| 合并稿（必读） | `~/.dc-platform/memory/work-log/YYYY-MM-DD.md` |
| 各机原文 | `~/.dc-platform/memory/work-log/hosts/<new-mac\|old-mac>/` |
| 本机习惯落盘 | `CHcode/.cursor/work-log/`（脚本会导出到 hosts） |
| 正式日报（权威） | `~/.dc-platform/memory/work-log/reports/YYYY-MM-DD-日报.md`（并镜像到本机 `.cursor/work-log/reports/`） |

## 日报流程（生成 → 记录）

1. 检索**当日**用户全部交办（transcript grep / 会话记忆）
2. 按模板写 `【今日结果】` 3 条左右，每条 20～30 字
3. **落盘**：`CHcode/.cursor/work-log/reports/YYYY-MM-DD-日报.md`
4. **同步**：更新 `.cursor/work-log/YYYY-MM-DD.md` 的 `## 完成` / `## 阻碍` / `## 明日`
5. 无交办的工作日：可不生成，或写「无交办」一条

## 日报模板

```markdown
# 日报 · 又初·YYYY-MM-DD

[REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:日报] [DATE:YYYY-MM-DD]
> 提交人: 又初 · 工号: DN6517 · 岗位: 后端 BE · 层级: L1

## 【今日结果】
- [TQ-002 | DMP系统] ……（20~30字），已完成；

## 【死锁阻碍】
- 

## 【专项复盘】
- 

## 【明日动作】
- TOP1: …（截止：下一工作日）
```

规则：

- 仅**工作日**生成；法定假日跳过（除非用户显式要求）
- `【明日动作】` 指**下一个工作日**（跳过周末与法定假）
- 每条约 **25~45 字**；通常 3 条
- **语气：通俗但正式（主人 2026-07-15 定稿）**——读者是部门/主管非开发。
  - 术语翻业务说法：`dws_session_duration_d`→「停留时长汇总表」；`attribution_flag=0`→「归因标识为0/未开启」；`is_valid/duration_bucket`→「有效标识/时长档位」；`ETL`→「数据加工」。
  - **区间/代码记号直出=黑话**：`[5,60)`→「5 秒~1 分钟」；`(1800,43200]`→「30 分钟~12 小时」；`col_list/PK`→「字段清单/主键」；表名、海豚宏不进正文。
  - **通俗 ≠ 口语**：保持书面日报语气，禁俚语（「根子上/聊了三轮/没写死/搞定」）→ 用书面词（「根因/经三轮联评/暂未固化·可配置/已完成」）。
  - 禁「术语罗列式」（如「sid宽表原地加列is_valid/五档/source_type」）→ 改「会话表新增『有效标识、时长档位、来源』等字段」。

## 周报开工前（必读，禁止跳过）

写周报 /「上周总结」前**按序读完**再动笔：

0. **`project_youchu_workbook_tasks.md`**（又初当前主责；若用户刚贴新簿先更新该文件）
1. 本 playbook（本节 + 日报内容铁律）
2. `reference_work_calendar_cn.md` → 算自然周边界与有效工作日天数
3. `.cursor/work-log/YYYY-Www.md`（若有）+ 该周各 `YYYY-MM-DD.md`
4. `.cursor/work-log/reports/` 该周日报与上一份周报样例（如 `2026-W26-周报.md`）
5. 狂人派单：`task_provenance.jsonl` / `youchu_ai_inbox.jsonl`（去重，**正文禁 bus#**）
6. `lessons/_index.md` 仅供【卡点】

## 周报内容铁律（与日报对齐，主人 07-03/07-07/07-08）

- **只写数据工作**（ETL/核查/发布/归因/排行/口径等）
- **禁止**写入：机器人/TG/poller/通道运维、VPN、本机环境迁移、IDE 唤醒链路（用户明确要求除外）
- **禁止** `bus#N` / `bus入#N`；写任务名/表名/专项
- 结果导向短句；不展开 SQL/长表名清单
- **通俗但正式**（同日报，主人 2026-07-15）：术语翻业务说法、书面语气、禁口语俚语
- 用户交办 + 狂人实活**同一套条目**，不单开「狂人附录」
- 合并该自然周**工作日**日报/work-log，去重按专项分条

## 周报模板

```markdown
# 周报 · 又初·YYYY-Www（MM-DD 周一 ~ MM-DD 周日）

[REPORT-ORG:天穹部门] [LEVEL:L1] [TYPE:周报] [DATE:提交日]
> 统计周期：自然周 Www · **有效工作日 N 天**（…）· 周日/法定假说明

## 【本周完成】
### <专项名>
- ……（任务名表述，已完成/进行中语义清晰）

## 【卡点】
- ……

## 【周日 / 法定假】
- ……

## 【下周计划】Wxx（MM-DD 周一 ~ MM-DD 周日）
> 仅排工作日 TOP3；P0/P1；遇假注明

| 优先级 | 事项 |
|--------|------|
| P0 | … |

## 【日报索引】
- [MM-DD](YYYY-MM-DD-日报.md) 或一句补缺说明

## 【一句话给周会】
> **上周**…；**卡点**…；**本周**…
```

## 收尾

- 缺当日流水 → 生成日报时**一并创建/更新** `.cursor/work-log/YYYY-MM-DD.md`
- 正式日报/周报必存 `.cursor/work-log/reports/`
- **周日或下周一**：刷新 `.cursor/work-log/YYYY-Www.md` + `reports/YYYY-Www-周报.md`
- 写周报：合并该自然周各 `reports/*-日报.md`，去重按专项归纳
- 写周报前先读 `reference_work_calendar_cn.md` 算有效工作日天数
