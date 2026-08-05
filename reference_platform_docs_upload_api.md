---
name: 平台文档库 upload/raw API
description: POST /api/v1/platform/docs/upload 提交指标/分析文档；GET raw/{slug} 直读
type: reference
---

# 平台文档库 API（又初可用）

Base：`http://54.255.236.159:8012`  
Token：`.claude/database/dc-platform.json` → `token`（Bearer）

| 动作 | 方法 | 路径 |
|------|------|------|
| 列表 | GET | `/api/v1/platform/docs`（可不带 token） |
| 正文 | GET | `/api/v1/platform/docs/raw/{slug}`（需 token） |
| 上传 | POST | `/api/v1/platform/docs/upload` multipart（需 token；**非 admin 亦可**，2026-08-05 已验证） |
| 删除 | DELETE | `/api/v1/platform/docs/{id}`（视权限；探测稿可删） |

上传字段：`file`、`slug`、`title`、`kind`=`html|md`、`description`、`sort_order`。  
同 slug 再传即覆盖。库页 `/library/{slug}`。

本地脚本 `dc-platform-server/scripts/publish-doc.sh` 默认读 `~/.claude.json` admin token；又初日常用 `dc-platform.json` 的 token 直调即可。

指标分析格式见 [[feedback_metric_analysis_doc_template_and_upload]]。
