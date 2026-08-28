# OneHR 打卡 · old-mac 接入

双机通过 `youchu-memory` 同步脚本；**密钥不进库**，每台机各自维护 `~/.dc-platform/config/onehr.env`。

## 1. 拉最新 memory

```bash
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

sync 会自动把仓内 `scripts/onehr_*` 覆盖到 `~/.dc-platform/scripts/`（与 `load-memory-context.sh` 同机制）。

## 2. 本机配置（仅首次）

```bash
cp ~/.dc-platform/config/onehr.env.example ~/.dc-platform/config/onehr.env
chmod 600 ~/.dc-platform/config/onehr.env
# 编辑 ONEHR_PASSWORD、ONEHR_SCREENSHOT_DIR（Telegram 设备页截图目录）
```

`memory/.env.host` 建议设 `WORKLOG_HOST_ID=old-mac`。

## 3. 安装调度（KeepAlive）

```bash
bash ~/.dc-platform/scripts/install-onehr-checkin-launchd.sh
python3 ~/.dc-platform/scripts/onehr_checkin_scheduler.py --show-plan
```

## 4. 验收

```bash
bash ~/.dc-platform/scripts/onehr_checkin_run.sh --dry-run
tail -f ~/.dc-platform/onehr/logs/scheduler.log
```

## 5. 卸载

```bash
bash ~/.dc-platform/scripts/uninstall-onehr-checkin-launchd.sh
```

## 注意

- **new-mac / old-mac 只应有一台** 装 `com.youchu.onehr-checkin`，避免重复打卡。
- 极客真实打卡仍关（`JIKE_CHECKIN_ENABLED=false`）；TG 绿点计划与 OneHR 独立。
- 规则详见 `scripts/docs/onehr_checkin_auto.md`。
