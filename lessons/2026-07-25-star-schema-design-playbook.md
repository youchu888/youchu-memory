---
date: 2026-07-25
tags: [star-schema, design, dws, ads, playbook]
severity: medium
domain: sql
---

# 星型模型设计 playbook 已沉淀（私聊#227）

## 背景

主人要求又初深入学习星型模型，后续设计 DWS/ADS 分析模型时要直接套用。知识分散在 content_rank v2.1 HTML、现网 design.md、平台知识库。

## 正确做法

1. **设计前**读 canonical playbook：`.claude/database/playbooks/star_schema_design.md`
2. **权威案例**：`omdb/projects/content-rank/design/content_rank_star_schema_design_v2_20260721.html`（star schema v3.3）
3. stage 2 `design.md` 必须含「星型模型设计」章节（粒度 / 维度来源 / 扫描计划 / 度量分型 / 不落表衍生 / 反模式自检）
4. 先判断范式：汇总报表→星型；当前态标签/uid×dt 明细→非星型

## 核心口诀

**单次 scan 建事实 · 少量 dim JOIN · 退化维 inline · bitmap UV · 查询层算 rank · 不存废列。**

## 验证

- 新 design 能填完 playbook §5 checklist 且无双扫/雪花/rank 落表/SUM(日UV) 等反模式

## 关联

- Playbook：`.claude/database/playbooks/star_schema_design.md`
- 案例：`dws_app_user_d_h`、`dws_app_order_d_h`、`ads_content_rank_*`、`dws_video_account_d_d`
- 反例：`dim_content_all` 废除、`dws_user_tag_d_d` 非星型
