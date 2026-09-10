---
date: 2026-09-10
tags: [daily-report, work-log, lessons, agent-speed]
severity: high
domain: ops
---

# 闲时沉淀当日实活；用时只快速检索，禁止临时重翻半仓

## 背景

主人 2026-09-09：补日报本机活（设计评审、数据核查）时又初先扫 transcript / 找报告 / 挂后台检索，把「改几行 + 贴正文」拖成排查。次日纠正：这类事应闲暇时沉淀，要用时快速检索。

## 坑 / 错误做法

- 写日报 / 被催进度时才去翻全量 transcript、find 报告、重推设计结论
- 活干完不写 work-log / lesson / 任务板，等晚上再「考古」
- 把「确认事实」做成半仓扫描，再改稿、还不贴聊天

## 正确做法

1. **闲时（任务收尾 / 空档）**：当日实活立刻落
   - 一句话进 `work-log`（本机 hosts 或当日 md）
   - 有坑/口径 → lesson + `_index`；核查规则 → playbook
   - 设计评审结论用 3～5 条 bullet 落盘，勿只留在会话里
2. **用时（写日报 / 「加进去」/ 「发这里」）**：只读索引与当日流水
   - `work-log` 合并稿 / `reports/日报-*.md` / lessons `_index` 匹配行
   - **禁止**再扫半仓 transcript 当主路径
   - 改完 **立刻贴聊天正文**（落盘不算交付）
3. 缺流水时：最多补扫**当日**相关 session 标题，不扩到多日全库

## 验证

催「加本机活 / 发这里」时：≤1～2 次短读（work-log 或已有定稿）→ 改稿 → 对话贴出全文；无长时间 find/全 transcript 考古。

## 关联

- 规则：`.cursor/rules/agent-speed.mdc`（上下文瘦身、脚本优先）
- 日报：`.cursor/rules/daily-report.mdc`；落盘 `work-log/reports/日报-*.md`
- 教训同日：日报改完须先贴聊天，勿只改文件
