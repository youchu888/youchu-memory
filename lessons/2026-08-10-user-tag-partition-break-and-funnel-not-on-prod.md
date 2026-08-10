---
date: 2026-08-10
tags: [user-tag, partition, 断流, datacheck]
severity: high
domain: datacheck
---

# 用户标签宽表须盯连续分区；单日暴增后次日归零优先当断流

## 背景

全链路扫标签：`dws_user_tag_d_d` 在 2026-08-06 约 12.8 亿行，08-05 仅 26 行，08-07～08-09 为 0。工作簿亦记「prod 未稳定上线 / 等验数」。

## 坑 / 错误做法

- 看到历史某日有巨量就报「标签已上线正常」
- 不查近 N 日 `GROUP BY dt` 连续性

## 正确做法

1. `SELECT dt, COUNT(*) FROM dws.dws_user_tag_d_d WHERE dt >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY) GROUP BY dt`
2. T-1=0 且近几日不连续 → 断流/未跑通，写入核查结论与明日动作
3. 单日行数数量级突变（百万→十亿或反过来）单独标 WARN，再查任务实例

大漏斗 `dws_app_event_funnel_d_d` 同理：prod/test 无表则标「未上线」，勿与其它 funnel 表名混淆。

## 验证

T-1=2026-08-09：tag=0；event_funnel 表不存在。

## 关联

- 工作簿：用户标签跟踪；YC-FUNNEL-001 进行中
- 报告：`reports/youchu_full_chain/validate_all__2026-08-09__20260810_191802.md`
