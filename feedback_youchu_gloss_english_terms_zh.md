---
name: youchu_gloss_english_terms_zh
description: 对主人说话时，英文技术名词后紧跟中文翻译
type: feedback
---

# 英文名词后带中文翻译（主人 2026-09-05）

## 规矩

对主人（本会话 / TG）写进展时：**英文技术名词后面立刻用括号带上对应汉字**，不要只甩英文标记。

例：`metric（指标）` · `wide（宽表）` · `slot（业务日分区）` · `DONE（完成）` · `filter（过滤）` · `EXIT（退出）`

## 常见对照（大漏斗 / 跑数）

| 英文 | 中文 |
|------|------|
| slot | 业务日分区 / 数据段 |
| task_dt / --dt | 任务日 |
| metric / stage_metrics | 指标长表阶段 |
| wide | 宽表阶段 |
| filter | 过滤条件 |
| DONE | 完成 |
| FAIL_METRIC / FAIL_WIDE | 指标阶段失败 / 宽表阶段失败 |
| EXIT | 退出 |
| sandbox | 沙箱 |
| yarn / application | YARN 应用 |
| progress / reply / ACK | 进度 / 结案回复 / 收到确认 |
| dwd.*_r | dwd 层带 _r 的事件表 |

## 反例

`metric → wide, filter 全空，盯到 DONE`（主人看不懂英文标记）

## 正例

`metric（指标）→ wide（宽表），filter（过滤）全空，盯到 DONE（完成）`
