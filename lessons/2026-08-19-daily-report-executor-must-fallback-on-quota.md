---
date: 2026-08-19
tags: [daily-report, cursor-executor, quota, launchd]
severity: high
domain: ops
---

# 日报定时能唤醒，但 executor 额度耗尽不降级 → 等人催

## 背景

2026-08-19：21:20 flush、21:30 wake、21:45 fallback 都跑了。`cursor-executor` 从 21:31 起对 `composer-2.5` 连打 6 次，全是 `resource_exhausted`，稿没写成。私聊「日报呢」同样撞额度；TG Bot 有 fallback 链，21:51 换成 `composer-2.5-fast` 才写完推送。

## 坑 / 错误做法

1. 定时链路当成「没跑」——其实 launchd + wake_feed 是通的，断在 **写稿进程死磕一个模型**。
2. `executor.env` 里有 `CURSOR_MODEL_FAST`，但 `cursor-executor-run.sh` 没导出 `AGENT_BUS_CURSOR_MODEL` / `FALLBACK`，executor 永远用默认 `composer-2.5`。
3. 额度耗尽仍对同一模型重试 3 次（30s/60s backoff），21:30 与 21:45 各一轮，空耗约 20 分钟且不私聊告警。
4. `prepare_daily_report_sync.sh` 在 `set -o pipefail` 下 `grep '^- '` 零命中会 exit 1，agent 第一步就失败（hosts 文件在但没有 `- ` 条目时）。

## 正确做法

1. 工作模型用 Cursor **`auto`**（按任务路由，不要锁死 composer-2.5）。
2. executor `_run_work_with_retry`：命中 `resource_exhausted` / quota **立刻换链上下一个**（auto → composer-2.5-fast → composer-2.5），不要同模型空转。
3. `cursor-executor-run.sh` 导出 `AGENT_BUS_CURSOR_MODEL=auto` 与 `AGENT_BUS_CURSOR_FALLBACK`。
4. 写稿与补推都失败时，给 ALLOWED_USERS 发一条失败私聊，禁止静默。
5. 同步脚本：`grep -c ... || true`，零 bullet 不算失败。
6. 改完 `launchctl kickstart` executor 与 tgbot，确认日志 `work=auto`。

## 验证

```bash
python3 -c "import sys; sys.path.insert(0, '$HOME/Library/Application Support/youchu-agent-bus/python'); from agent_bus_cursor_executor import _model_chain, _is_quota_fail; assert 'composer-2.5-fast' in _model_chain('composer-2.5'); assert _is_quota_fail('resource_exhausted', 1)"
launchctl print gui/$(id -u)/com.youchu.cursor-executor | awk '/state =|pid =/'
# 次日看 cursor_executor.log：start DAILY_REPORT 后若 2.5 失败，应立即 fallback 2.5-fast，而不是 3 次同模型
```

08-19 当日：你催后 TG 降级写稿，21:55 已推私聊。

## 关联

- `~/Library/Application Support/youchu-agent-bus/python/agent_bus_cursor_executor.py`
- `cursor-executor-run.sh`
- `~/.dc-platform/scripts/prepare_daily_report_sync.sh`
- lesson `2026-08-14-daily-report-executor-must-parse-DAILY_REPORT.md`（解析已修好；本次是额度）
