---
date: 2026-07-08
tags: [daily-report, feedback, bus, naming]
severity: high
domain: ops
---

# 日报禁止写 bus 编号，必须写任务名

## 背景

主人多次纠正日报/汇报文案（约 07-03、07-07）：不要写 `bus#xxxx`，要把具体工作内容/任务名写出来；另勿把机器人通道运维塞进日报。此前只留在 transcript，**未写入** `daily-report.mdc` / lesson，导致又重复踩坑。

## 坑 / 错误做法

- 日报写 `狂人·bus#3494 …`、`bus#3305` —— 外行人不知对应哪条活
- 规则文件仍写「可点明 `bus#N`」——与主人钦定冲突
- 只「口口相传」不存档 → 新会话又写编号

## 正确做法

1. 日报 / 对主人汇报：**写任务名或专项**（例：内容排行 v1.10 宽表骨架、归因看板 metrics 断流）
2. `bus_id` 仅内部去重、agent-bus ack/reply 使用，**不出现在日报正文**
3. 狂人相关条目前缀可用 `狂人·`，后面接任务名，不加编号
4. 改完同步：`.cursor/rules/daily-report.mdc` + 本 lesson + `_index.md`

## 验证

下一份日报全文搜索无 `bus#`；每条结果能独立看懂在干什么。

## 关联

- 规则：`.cursor/rules/daily-report.mdc`
- 主人纠正 transcript：`3c30c1aa…`（07-03）、`8bfa26bc…`（07-07）
