# 补丁：工作簿进展 · 有入站才回 · 群或 bus

**仓库**：`youchu-memory`（`omdb/tgbot/` 不入 CHcode git，走本补丁）

## 旧 Mac 生效

```bash
bash ~/.dc-platform/memory/scripts/apply_tgbot_workbook_no_instant_ack.sh
```

## 文件

| 相对路径 | 作用 |
|----------|------|
| `workbook_progress_service.py` | T-1 探针 + supplemental |
| `group_workbook_progress_handler.py` | 真群消息回群；真 bus 入站 `reply_workbook_via_bus`；**废止闹钟发群** |
| `workbook_trigger_watcher.py` | 扫 tg_status + bus inbox；不调 daily_fallback |
| `scripts/post_workbook_progress_to_group.py` | 手动发群须 `--file` |
| `data/workbook_supplemental.json` | 自开项 |

## 2026-09-05 主人钦定

群收不到就不要闹钟往群里回；走 bus。收到清单后按实查进度 reply，禁止秒回罐头。
