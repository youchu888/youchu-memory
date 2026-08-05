---
name: 需求指标分析必须按大漏斗模板并上传文档库
description: 每个需求分析/指标文档对标 metric_big_funnel_event_dictionary；写完 POST upload 提交平台文档库
type: feedback
---

# 需求指标分析文档格式（主人 2026-08-05）

对标线上模板：[大漏斗事件字典](http://54.255.236.159:8012/library/metric_big_funnel_event_dictionary)（slug=`metric_big_funnel_event_dictionary`）。

**与「数据字典四栏表」分开**：`feedback_data_dictionary_format` 只管字段清单；**需求分析 / 指标口径文档**必须用本模板（html 或 md 均可，推荐 html 保留色标）。

## 固定章节（顺序勿乱）

0. 数据链路与源表现状（flow + meta 表：主源/缺口/时间字段）
1. 输出表逐字段规则（1.1 整表 → 1.2 维度 → 1.3 属性 → 1.4 指标；多表则 1B…）
2. 已知数据质量问题（err / warn / ok）
3. 需产品确认的事项（红底问产品 / 蓝底初稿 / 黄底待填；已确认绿底+✅）
4. 数据侧已定（表结构、分区、写入、调度、主体去重等，不占产品确认位）

色标：红=`ask`、蓝=`draft`、黄=`todo`；无底色=实测或已定。

本地骨架：`.claude/database/templates/metric_analysis_skeleton.html`  
完整范例缓存：`.claude/database/templates/metric_analysis_template_from_big_funnel.html`

## 必须上传平台文档库

权限已开：又初（非 admin）可 `POST /api/v1/platform/docs/upload`（multipart：`file`/`slug`/`title`/`kind`/`description`/`sort_order`）。

```bash
# token：.claude/database/dc-platform.json
curl -sS -X POST -H "Authorization: Bearer $TOKEN" \
  "http://54.255.236.159:8012/api/v1/platform/docs/upload" \
  -F "file=@xxx.html" -F "slug=metric_xxx" -F "title=…" \
  -F "kind=html" -F "description=…" -F "sort_order=10"
```

读正文：`GET /api/v1/platform/docs/raw/{slug}` + Bearer。  
库页：`http://54.255.236.159:8012/library/{slug}`。

**何时写**：新需求对齐后、Stage1/2 前后；大活分析定稿必须上传，禁止只留本地。

**slug 约定**：`metric_<主题>`，如 `metric_page_visit_analysis`。

## Why

主人钦定：每个需求分析都按大漏斗那篇写，指标文档都交到开发平台文档库；上传接口已对开发者开放。
