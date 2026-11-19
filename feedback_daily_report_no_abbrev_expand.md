# 日报禁内部简写：自动推送与 IDE 同一标准

**来源**：多次纠正「不要简写」；2026-11-19 再钉——old-mac 自动推的稿也必须展开，与 new-mac 改定标准一致。

## 问题根因（不是「规矩没同步」）

1. **规矩文件双机已共用**（memory git + `.cursor/rules/daily-report.mdc`）
2. **old-mac 自动链路以前不读规矩**：
   - 21:30 wake 提示只写「只写已完成」，未写禁简写
   - 21:45 `auto_draft_daily_report.py` 只从 work-log **截短拼装**，流水里的「影子/冒烟/对平」原样进 TG
3. 你在 new-mac 对话里纠正后改的是本地定稿；**已推 TG 不会自动重发**

## 正确做法（两边同一标准）

正文禁止内部简写，必须展开成主管能看懂的书面说法。常见对照：

| 禁止 | 写成 |
|------|------|
| 物化稿 | 加工脚本 |
| 影子 / 建影子 | 对照表 / 建对照表 |
| 冒烟 | 验证出数 |
| 对平 | 核对对齐 |
| 应用维 / 页面维 / 订单维 | 应用/页面/订单维度表 |
| 首灌 | 首次灌数 |
| 微差 | 轻微差异 |
| 七步 | 开发平台各阶段 |
| 字典号版 | 按字典编号口径 |
| 核清收编 | 清理归并 |

## 已落硬闸（自动路径）

1. `memory/scripts/auto_draft_daily_report.py`：定稿前 `_expand_jargon`
2. `daily-report-wake.sh`：wake 提示显式写「禁简写 + 展开」
3. 权威机仍是 **old-mac**；改定后若要换 TG 稿须 `--force` 重推

## 关联

- 规则：`.cursor/rules/daily-report.mdc`
- 红线续篇：`pinned/40-daily-report-no-abbrev.md`
- lesson：`lessons/2026-11-19-日报禁简写须进自动定稿与wake.md`
