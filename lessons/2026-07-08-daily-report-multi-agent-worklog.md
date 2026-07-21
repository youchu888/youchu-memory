---
date: 2026-07-08
tags: [daily-report, work-log, multi-agent, feedback]
severity: high
domain: ops
---

# 日报必须汇总多 Agent 流水，勿只写当前会话

## 背景

主人指出日报漏项：「其他 agent 的内容呢？我不是还统计了一个归因规则吗」。归因出数规则 + HTML 手册在别的 Cursor 会话完成，当前会话写日报时只扫了本对话。

## 坑 / 错误做法

- 只根据**当前** transcript 写 `【今日结果】`
- 不读 `.cursor/work-log/YYYY-MM-DD.md`
- 不扫当日其它 `agent-transcripts/<id>/` 的用户交办

## 正确做法

写日报前按序：

1. 读 **`CHcode/.cursor/work-log/当日.md`**（多 Agent 收尾应已 append）
2. 扫当日所有 transcript 的用户消息（至少列任务清单）
3. 读狂人派单（provenance / inbox），与上者去重
4. **任务收尾时**立刻 append 当日 work-log（含路径产物），不要等 21:30

每条结果用任务名，禁止 `bus#`。

## 验证

日报条数能覆盖：报备归因、看板推送、出数规则手册、排行骨架/撤回、metrics 断流进展等当日实活，不只当前窗一句。

## 关联

- `feedback_work_log_multi_agent_reports.md`
- `.cursor/rules/daily-report.mdc`
- `lessons/2026-07-08-daily-report-no-bus-id.md`
- 当日流水：`CHcode/.cursor/work-log/2026-07-08.md`
