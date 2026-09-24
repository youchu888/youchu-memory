---
date: 2026-08-09
tags: [tgbot, workbook-progress, mysql, launchd, dm-spam]
severity: high
domain: ops
---

# 工作簿拦截私聊刷屏：launchd 找不到 mysql + 拦截未去重

## 背景

主人 TG 私聊被「发群前核查未通过，已拦截」刷屏（约每 2 分钟一次）。根因不是真没分区，而是 bot 进程探针失败。

## 坑 / 错误做法

1. `workbook_progress_service._mysql_row` 写死调用 `mysql`；launchd PATH 无 `/usr/local/opt/mysql-client/bin` → `FileNotFoundError` 被吞掉，快照全空。
2. verify 失败后 `_release_brief_inflight` + DM，**不记已通知**；`_DATE_COOLDOWN_SEC=120`，09:01–11:59 兜底每 20s 轮询 → 冷却一过再 DM。
3. 重启时残留 `brief_inflight` 被 `already_posted_for_date` 当成已完成，整天卡住。

## 正确做法

1. 探针用 `MYSQL_BIN`（`.env` 已有）+ Homebrew 常见绝对路径回退；失败打日志，禁止静默空结果。
2. `_env.sh` / `launchd-start.sh` PATH 前置 `mysql-client/bin`。
3. verify 拦截：**同一天私聊只发一次**（`verify_blocked_notified`）；仍可静默重试，成功发群后清标志。
4. `brief_inflight` 超过 300s 自动过期释放。

## 验证

- 直连 prod：`session_duration_user_d` / `visit_d_d` 均有 `2026-08-08` 分区。
- 修后 `verify_progress_before_group_post` → True；`posted date=2026-08-09 source=daily_fallback`；此后无 `verify blocked` DM。

## 关联

- 脚本：`omdb/tgbot/workbook_progress_service.py`、`group_workbook_progress_handler.py`、`_env.sh`
- 配置：`omdb/tgbot/.env` → `MYSQL_BIN=/usr/local/opt/mysql-client/bin/mysql`
