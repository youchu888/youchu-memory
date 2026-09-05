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
| `workbook_progress_service.py` | T-1 探针 + supplemental + 单条正文；禁印「禁止秒回模板」 |
| `group_workbook_progress_handler.py` | 去掉精简秒回/双条 follow-up；**09:08** 才兜底；禁写死 1/2 条 |
| `scripts/post_workbook_progress_to_group.py` | dry-run / 手动发群对齐 |
| `data/workbook_supplemental.json` | 自开项（uid_map/漏斗/指标库） |

## 2026-09-05 再修（主人感觉仍秒回）

根因：`maybe_daily_fallback` 在 **09:01** 用 `fallback_workbook_template` 写死「1.页面 2.归因」，`message_id=0`，没吃当日工作簿原文。正文还印着「禁止秒回模板」。

现规则：
- 兜底窗口 **09:08–11:59**（给 09:00 真簿进站留窗口）
- stub 不含编号【又初】项；未进站则走 task 板+自开，并写明「原文未进站」
- 识别并丢弃旧 1/2 条自造模板，禁止写回 `workbook_last_full.json`

## 验证

```bash
cd ~/Desktop/CHcode/omdb/tgbot
# 期望：无「禁止秒回模板」；09:01 不在兜底窗口
```
