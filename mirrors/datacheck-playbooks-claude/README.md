# 表级核查剧本说明

用于维护每张表的专属核查“小技能”。**剧本是从 ETL 代码里提炼的核对规则，核查认可后必须写回剧本，下次 `/datacheck` 直接复用。**

## AI 工作流（必遵守）

1. 开工：读本 README → 打开 `playbooks/<db>.<table>.md`
2. 按 `part_01`…顺序跑 SQL，报告落 `reports/<表名>/`
3. 收尾：**本次新规则增补进剧本** + 文首变更记录一行（详见 `.cursor/rules/datacheck-playbook.mdc`）
4. 踩坑另写 `lessons/`；剧本记**可执行核查步骤**，二者不替代

套表/逐层核查：先读 `datacheck_layered_verification.md`。

## 文件命名规则
- 每张表一个文件。
- 文件名直接使用全限定表名：`数据库名.表名.md`
- 示例：`ads.ads_product_day_stat_d.md`
- 套表/流程剧本：`dws.dws_register_attribution_gray_verify.md`（归因灰度三条验收，非单表行数核查）

## 已登记剧本（摘录）

| 文件 | 用途 |
|------|------|
| `_ops_server_monitor_incident.md` | server_monitor / prod FAIL 告警处置（非表级 datacheck） |
| `_ops_dolphinscheduler_workflow_update.md` | 海豚 wf PUT / release / schedule SOP |
| `dws.dws_register_attribution_gray_verify.md` | 灰度 app channel_apply 三条验收 |
| `datacheck_layered_verification.md` | 套表逐层核查 |

## 每个剧本必须包含的内容
1. 表标识
2. 业务名
3. 表状态
4. 参数约定（必填、选填）
5. 核查 parts 列表
6. 每个 part 的 SQL 模板
7. 输出字段说明
8. 判定规则
9. 报告落地约定

## 核查 part 命名规范
- `part_01_xxx`
- `part_02_xxx`
- `part_03_xxx`

建议使用稳定语义，例如：
- `part_01_total_vs_subtotal`
- `part_02_detail_reconciliation`
- `part_03_metric_sanity`
- `part_04_exception_sampling`

## 参数约定
- `dt`：常见的统计日期参数，通常必填
- `app_id` / `app_code`：应用标识，通常选填
- 如果缺少关键参数，`/db` 只追问一个关键问题

## SQL 模板约定
- SQL 使用全限定表名
- 只记录该表专属或高度相关的 SQL
- 通用写法（如 `COALESCE`、条件聚合等）放入 `knowledge.md`
- 如果某个 part 依赖其他来源表，应在剧本中明确写出来源表和用途

## 程序绑定约定
- 若某张表已有稳定生产 SQL / ETL，playbook 必须记录绑定处理程序路径。
- 来源核查类 part 应尽量标注对应程序中的逻辑块（如 CTE、子查询、聚合阶段），便于 `/datacheck` 直接复用。
- 不要求把整段程序复制进剧本，但至少要写清：来源表、目标字段、对齐粒度、关联键、过滤条件、核心聚合逻辑、异常判定。
- 若程序现状与已确认业务口径不一致，剧本中必须显式记录“待核对点”，不能静默覆盖。

## 输出与报告约定
- 只要执行表级核查，默认展示被核查数据的 markdown 表格
- 每个 part 需给出单独结论：通过 / 失败 / 跳过
- 核查结果默认保存到：`.claude/database/reports/<full_table_name>/`
- 所有核查报告默认按以下顺序组织：
  1. **结论**：先给总体结论，明确通过/不通过及核心问题
  2. **核查大类汇总**：按大类汇总结果，例如总分核查、来源核查、异常值核查，每类都要有数据
  3. **逐条规则结果**：列出每条核查规则、核验范围、异常行数/样本数、结论，不能只写文字判断
  4. **问题与处理建议**：对发现的问题给出可执行处理办法，并说明建议依据
- 如果报告中引用抽样证明，需同时给出“正常样本”和“异常样本（如存在）”，且样本必须带目标值与来源值/分项值的并排数据。
