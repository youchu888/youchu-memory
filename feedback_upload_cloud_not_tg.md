---
name: feedback_upload_cloud_not_tg
description: 用户说「上传云端」= 填报 HTML 对应 API，与 TG 无关
type: feedback
---

# Feedback：上传云端 = 填报 HTML，与 TG 无关

**来源**：2026-09-29 主人钉死——「上传云端就是用我发的 html 传，和 tg 没有关系」

## 唯一正确理解

- **上传云端** = 用 `~/Desktop/CH/技术体系_工作报告填报.html` 的「上传云端」同一条路  
  （API：`https://ep.jsyyds.com/api/v1/report/submit`；凭据：同目录 `config.js`）
- 命令行等价：`.cursor/scripts/upload_work_report.py --config /Users/mac/Desktop/CH/config.js`
- **与 Telegram / `post_daily_report_to_dm.py` 完全无关**；说「上传云端」时禁止跑 TG 推送

## 对照

| 用户说法 | 动作 |
|----------|------|
| 上传云端 / 按这个上传 | 定稿原样落盘 → `upload_work_report.py`（填报 HTML 同一 API） |
| 推 TG / 发私聊 | 仅在用户明确说推 TG，或权威机自动日报链路时，才跑 `post_daily_report_to_dm.py` |

二者分开；说云端只做云端。
