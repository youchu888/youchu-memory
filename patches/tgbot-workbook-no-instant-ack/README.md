# 补丁：工作簿进展禁秒回 · 清单主责+自开实责 · T-1 实查单条

**仓库**：`youchu-memory`（`omdb/tgbot/` 不入 CHcode git，走本补丁）

## 旧 Mac 生效

memory sync 拉到本补丁后：

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_workbook_no_instant_ack.sh
```

会：备份 → 覆盖 4 个文件 → smoke → `restart.sh`

## 文件

| 相对路径 | 作用 |
|----------|------|
| `workbook_progress_service.py` | T-1 探针 + supplemental + 单条正文 |
| `group_workbook_progress_handler.py` | 去掉精简秒回/双条 follow-up |
| `scripts/post_workbook_progress_to_group.py` | dry-run / 手动发群对齐 |
| `data/workbook_supplemental.json` | 自开项（uid_map/漏斗/指标库） |

## 验证

```bash
cd ~/Desktop/CHcode/omdb/tgbot
.venv/bin/python scripts/post_workbook_progress_to_group.py --dry-run
# 期望十余秒后出一条；含页面/归因 T-1 数字 + supplemental；无「精简·补发」
```
