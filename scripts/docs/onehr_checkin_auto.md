# OneHR 考勤自动打卡

## 规则（与极客打卡一致）

| 类型 | 时间 | 星期 |
|------|------|------|
| 上班卡 | 9:30–10:00 | 周一至周六 |
| 下班卡 | 22:00–22:30 | 周一至周五 |
| 下班卡 | 19:00–19:30 | 周六 |
| 周日 | 不打卡 | — |

**调度方式**：`onehr_checkin_scheduler.py` 每天在窗口内**随机**选一个时刻（同 `jike_checkin_watcher.py`），到点再截图上传。不是固定 cron 多点重试。

截图失败**禁止**回退目录里几天前的 PNG。只上传 3 分钟内新截的图。窗口定位用 CoreGraphics，不走 System Events。

## 组件

| 文件 | 作用 |
|------|------|
| `onehr_checkin_scheduler.py` | 随机计划 + 守护循环 |
| `onehr_checkin_auto.py` | 登录 OneHR → API 上传 |
| `onehr_telegram_devices_screenshot.sh` | Telegram 设备页截图 |

## 配置

`~/.dc-platform/config/onehr.env` — 窗口变量名对齐极客 `JIKE_*_WINDOW_*` 语义。

## 命令

```bash
# 看今天随机计划几点打
python3 ~/.dc-platform/scripts/onehr_checkin_scheduler.py --show-plan

# 手动立即尝试（仍须 API 窗口开放）
bash ~/.dc-platform/scripts/onehr_checkin_run.sh --dry-run

# 安装 KeepAlive 调度
bash ~/.dc-platform/scripts/install-onehr-checkin-launchd.sh
```

日志：`~/.dc-platform/onehr/logs/scheduler.log`

## 与极客关系

- 极客真实打卡已关（`JIKE_CHECKIN_ENABLED=false`）→ 改 OneHR 网站打卡
- **绿点/TG 在线计划仍走极客那套时间窗**，勿混为一谈
- OneHR 调度独立，但**上下班窗口与星期规则与极客一致**
